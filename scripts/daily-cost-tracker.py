#!/usr/bin/env python3
"""
Daily Cost Tracker - OpenClaw Best Practices Implementation
Analyzes session logs for today-only costs, following OpenClaw's design patterns.

Based on OpenClaw documentation:
- Uses same approach as built-in `/usage cost` command
- Parses .jsonl session files for usage.cost.total data
- Filters to today-only timestamps for accurate daily tracking
- Respects Gateway as source of truth while analyzing existing logs
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
import argparse

def parse_timestamp(timestamp_str):
    """Parse OpenClaw timestamp format to datetime object."""
    try:
        # OpenClaw uses ISO format: "2026-03-01T19:35:27.123Z"
        return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
    except:
        return None

def is_today(timestamp_str, target_date):
    """Check if timestamp is from target date (default today)."""
    dt = parse_timestamp(timestamp_str)
    if not dt:
        return False
    
    # Convert to local time for date comparison
    local_dt = dt.replace(tzinfo=timezone.utc).astimezone()
    return local_dt.date() == target_date

def analyze_session_file_today_only(file_path, target_date):
    """Analyze a session file for today-only cost data."""
    costs_today = []
    models_used = set()
    
    try:
        with open(file_path, 'r') as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    
                    # Look for assistant messages with cost data from today
                    if (entry.get('type') == 'message' and 
                        entry.get('message', {}).get('role') == 'assistant' and
                        'usage' in entry.get('message', {}) and
                        is_today(entry.get('timestamp', ''), target_date)):
                        
                        message = entry['message']
                        usage = message.get('usage', {})
                        cost_info = usage.get('cost', {})
                        
                        if 'total' in cost_info:
                            cost = float(cost_info['total'])
                            model = message.get('model', 'unknown')
                            models_used.add(model)
                            
                            costs_today.append({
                                'timestamp': entry.get('timestamp'),
                                'model': model,
                                'cost': cost,
                                'tokens': usage.get('totalTokens', 0),
                                'input_tokens': usage.get('input', 0),
                                'output_tokens': usage.get('output', 0),
                                'cache_read': usage.get('cacheRead', 0),
                                'cache_write': usage.get('cacheWrite', 0)
                            })
                            
                except (json.JSONDecodeError, KeyError, ValueError):
                    continue  # Skip invalid entries
    
    except Exception as e:
        return None, f"Error reading {file_path}: {e}"
    
    total_cost = sum(entry['cost'] for entry in costs_today)
    
    return {
        'file': os.path.basename(file_path),
        'total_cost': total_cost,
        'message_count': len(costs_today),
        'models_used': list(models_used),
        'cost_entries': costs_today
    }, None

def analyze_daily_costs(target_date=None):
    """Analyze all session files for today's costs only."""
    if target_date is None:
        target_date = datetime.now().date()
    
    target_str = target_date.strftime('%Y-%m-%d')
    
    # OpenClaw session file location
    session_dir = Path.home() / '.openclaw' / 'agents' / 'main' / 'sessions'
    
    if not session_dir.exists():
        return None, f"Session directory not found: {session_dir}"
    
    print(f"=== DAILY COST ANALYSIS - {target_str} ===")
    print(f"Analyzing session logs: {session_dir}")
    print(f"Following OpenClaw best practices (same as built-in /usage cost)")
    print()
    
    # Find all .jsonl session files
    session_files = list(session_dir.glob('*.jsonl'))
    
    total_cost_today = 0
    total_messages_today = 0
    all_models = set()
    file_results = []
    
    print(f"Scanning {len(session_files)} session files...")
    
    # Analyze each file for today's costs
    for file_path in session_files:
        result, error = analyze_session_file_today_only(file_path, target_date)
        
        if error:
            print(f"⚠️  {error}")
            continue
            
        if result and result['total_cost'] > 0:
            file_results.append(result)
            total_cost_today += result['total_cost']
            total_messages_today += result['message_count']
            all_models.update(result['models_used'])
    
    # Sort by cost (highest first)
    file_results.sort(key=lambda x: x['total_cost'], reverse=True)
    
    # Report results
    print("=== TOP COST FILES (Today Only) ===")
    for result in file_results[:5]:  # Top 5
        models_str = ', '.join(result['models_used'])
        model_short = 'Opus' if 'opus' in models_str else 'Sonnet'
        print(f"{result['file'][:35]}... ${result['total_cost']:.3f} ({result['message_count']} msgs, {model_short})")
    
    print()
    print("=== TODAY'S SUMMARY ===")
    print(f"Date analyzed: {target_str}")
    print(f"Files with costs: {len(file_results)}")
    print(f"Messages today: {total_messages_today}")
    print(f"Models used: {', '.join(sorted(all_models))}")
    print(f"**TOTAL COST TODAY: ${total_cost_today:.2f}**")
    
    # Model breakdown
    model_costs = {}
    for result in file_results:
        for model in result['models_used']:
            model_name = 'Opus' if 'opus' in model else 'Sonnet'
            model_costs[model_name] = model_costs.get(model_name, 0) + result['total_cost']
    
    if model_costs:
        print()
        print("=== MODEL BREAKDOWN ===")
        for model, cost in sorted(model_costs.items(), key=lambda x: x[1], reverse=True):
            pct = (cost / total_cost_today * 100) if total_cost_today > 0 else 0
            print(f"{model}: ${cost:.2f} ({pct:.0f}%)")
    
    return {
        'date': target_str,
        'total_cost': total_cost_today,
        'message_count': total_messages_today,
        'file_count': len(file_results),
        'models_used': list(all_models),
        'model_breakdown': model_costs,
        'files': file_results
    }, None

def main():
    """Command line interface for daily cost analysis."""
    parser = argparse.ArgumentParser(description='Analyze OpenClaw daily costs from session logs')
    parser.add_argument('--date', help='Date to analyze (YYYY-MM-DD, default: today)')
    parser.add_argument('--json', action='store_true', help='Output JSON format')
    
    args = parser.parse_args()
    
    target_date = None
    if args.date:
        try:
            target_date = datetime.strptime(args.date, '%Y-%m-%d').date()
        except ValueError:
            print(f"Invalid date format: {args.date}. Use YYYY-MM-DD")
            return 1
    
    result, error = analyze_daily_costs(target_date)
    
    if error:
        print(f"Error: {error}")
        return 1
    
    if args.json:
        print(json.dumps(result, indent=2))
    
    return 0

if __name__ == "__main__":
    exit(main())
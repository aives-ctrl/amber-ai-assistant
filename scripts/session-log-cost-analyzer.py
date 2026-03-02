#!/usr/bin/env python3
"""
Session Log Cost Analyzer - Extract actual costs from .jsonl session files
This analyzes the real cost data that Anthropic reports back to OpenClaw.
"""

import json
import os
from datetime import datetime
from pathlib import Path

def analyze_session_file(file_path):
    """Analyze a single .jsonl session file for cost data."""
    total_cost = 0
    message_count = 0
    cost_entries = []
    models_used = set()
    
    try:
        with open(file_path, 'r') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    entry = json.loads(line.strip())
                    
                    # Look for messages with usage/cost data
                    if (entry.get('type') == 'message' and 
                        entry.get('message', {}).get('role') == 'assistant' and
                        'usage' in entry.get('message', {})):
                        
                        message = entry['message']
                        usage = message.get('usage', {})
                        cost_info = usage.get('cost', {})
                        
                        if 'total' in cost_info:
                            cost = float(cost_info['total'])
                            total_cost += cost
                            message_count += 1
                            
                            model = message.get('model', 'unknown')
                            models_used.add(model)
                            
                            # Store detailed cost info
                            cost_entries.append({
                                'timestamp': entry.get('timestamp'),
                                'model': model,
                                'cost': cost,
                                'tokens': usage.get('totalTokens', 0),
                                'input_tokens': usage.get('input', 0),
                                'output_tokens': usage.get('output', 0)
                            })
                            
                except json.JSONDecodeError:
                    continue  # Skip invalid JSON lines
                except Exception as e:
                    continue  # Skip other parsing errors
    
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return None
    
    return {
        'file': os.path.basename(file_path),
        'total_cost': total_cost,
        'message_count': message_count,
        'models_used': list(models_used),
        'cost_entries': cost_entries
    }

def analyze_all_session_files():
    """Analyze all session files from today."""
    session_dir = Path.home() / '.openclaw' / 'agents' / 'main' / 'sessions'
    today_str = "2026-03-01"
    
    # Find all .jsonl files modified today
    session_files = []
    for file_path in session_dir.glob('*.jsonl'):
        try:
            # Check if file was modified today
            mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
            if mtime.strftime('%Y-%m-%d') == today_str:
                session_files.append(file_path)
        except Exception:
            continue
    
    print(f"=== SESSION LOG COST ANALYSIS ===")
    print(f"Found {len(session_files)} session files from {today_str}")
    print(f"Analyzing files in: {session_dir}")
    print()
    
    total_cost_all = 0
    total_messages = 0
    all_models = set()
    file_results = []
    
    # Analyze each file
    for file_path in sorted(session_files, key=lambda x: x.stat().st_size, reverse=True):
        result = analyze_session_file(file_path)
        if result and result['total_cost'] > 0:
            file_results.append(result)
            total_cost_all += result['total_cost']
            total_messages += result['message_count']
            all_models.update(result['models_used'])
    
    # Sort by cost (highest first)
    file_results.sort(key=lambda x: x['total_cost'], reverse=True)
    
    # Report results
    print("=== TOP COST FILES ===")
    for result in file_results[:10]:  # Top 10
        models_str = ', '.join(result['models_used'])
        print(f"{result['file'][:40]}... ${result['total_cost']:.3f} ({result['message_count']} msgs, {models_str})")
    
    print()
    print("=== SUMMARY ===")
    print(f"Total files with costs: {len(file_results)}")
    print(f"Total messages analyzed: {total_messages}")
    print(f"Models used: {', '.join(sorted(all_models))}")
    print(f"**TOTAL COST FROM SESSION LOGS: ${total_cost_all:.2f}**")
    print()
    
    # Verification
    print("=== VERIFICATION ===")
    print("Auto-recharge amount: $10.77")
    accuracy = (total_cost_all / 10.77) * 100 if total_cost_all > 0 else 0
    print(f"Session log analysis: ${total_cost_all:.2f}")
    print(f"Accuracy: {accuracy:.1f}%")
    
    if accuracy > 95:
        print("✅ Excellent accuracy - session logs account for actual costs!")
    elif accuracy > 80:
        print("✅ Good accuracy - minor discrepancy likely from timing/rounding")
    else:
        print("⚠️ Low accuracy - may be missing cost sources")
    
    return total_cost_all, file_results

if __name__ == "__main__":
    analyze_all_session_files()
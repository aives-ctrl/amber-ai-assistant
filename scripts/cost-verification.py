#!/usr/bin/env python3
"""
Cost verification against actual Anthropic billing.
The auto-recharge happened at 11:23 AM, so costs after that are for the next billing cycle.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

def parse_timestamp(timestamp_str):
    """Parse OpenClaw timestamp format to datetime object."""
    try:
        return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
    except:
        return None

def analyze_costs_by_time_window():
    """Analyze costs in different time windows to match billing cycle."""
    session_dir = Path.home() / '.openclaw' / 'agents' / 'main' / 'sessions'
    
    # Auto-recharge happened at 2026-03-01 11:23 AM PST = 19:23 UTC
    billing_cutoff = datetime(2026, 3, 1, 19, 23, 0, tzinfo=timezone.utc)
    today_start = datetime(2026, 3, 1, 0, 0, 0, tzinfo=timezone.utc)
    
    costs_before_recharge = 0
    costs_after_recharge = 0
    messages_before = 0
    messages_after = 0
    
    print("=== COST VERIFICATION BY BILLING CYCLE ===")
    print(f"Billing cutoff: {billing_cutoff} (when auto-recharge triggered)")
    print(f"Actual recharge: $10.77")
    print()
    
    # Analyze main session file (biggest cost driver)
    main_session = session_dir / '59def9ab-0426-4034-b18a-80bbe8316ee1.jsonl'
    
    if main_session.exists():
        with open(main_session, 'r') as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    
                    if (entry.get('type') == 'message' and 
                        entry.get('message', {}).get('role') == 'assistant' and
                        'usage' in entry.get('message', {})):
                        
                        timestamp_str = entry.get('timestamp', '')
                        timestamp = parse_timestamp(timestamp_str)
                        
                        if timestamp and timestamp >= today_start:
                            message = entry['message']
                            cost_info = message.get('usage', {}).get('cost', {})
                            
                            if 'total' in cost_info:
                                cost = float(cost_info['total'])
                                
                                if timestamp <= billing_cutoff:
                                    costs_before_recharge += cost
                                    messages_before += 1
                                else:
                                    costs_after_recharge += cost
                                    messages_after += 1
                                
                except (json.JSONDecodeError, KeyError, ValueError):
                    continue
    
    # Add smaller session files (today only, before cutoff)
    other_costs_before = 0
    for file_path in session_dir.glob('*.jsonl'):
        if file_path.name.startswith('59def9ab'):  # Skip main file (already processed)
            continue
            
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    try:
                        entry = json.loads(line.strip())
                        
                        if (entry.get('type') == 'message' and 
                            entry.get('message', {}).get('role') == 'assistant' and
                            'usage' in entry.get('message', {})):
                            
                            timestamp_str = entry.get('timestamp', '')
                            timestamp = parse_timestamp(timestamp_str)
                            
                            if timestamp and today_start <= timestamp <= billing_cutoff:
                                cost_info = entry.get('message', {}).get('usage', {}).get('cost', {})
                                if 'total' in cost_info:
                                    other_costs_before += float(cost_info['total'])
                                    
                    except (json.JSONDecodeError, KeyError, ValueError):
                        continue
        except Exception:
            continue
    
    total_before_recharge = costs_before_recharge + other_costs_before
    
    print(f"=== MAIN SESSION (59def9ab...) ===")
    print(f"Before recharge: ${costs_before_recharge:.2f} ({messages_before} msgs)")
    print(f"After recharge:  ${costs_after_recharge:.2f} ({messages_after} msgs)")
    
    print(f"\n=== OTHER SESSIONS ===") 
    print(f"Before recharge: ${other_costs_before:.2f}")
    
    print(f"\n=== BILLING CYCLE VERIFICATION ===")
    print(f"Calculated (before 11:23 AM): ${total_before_recharge:.2f}")
    print(f"Actual auto-recharge amount:   $10.77")
    
    accuracy = (total_before_recharge / 10.77) * 100 if total_before_recharge > 0 else 0
    print(f"Accuracy: {accuracy:.1f}%")
    
    if 90 <= accuracy <= 110:
        print("✅ Excellent accuracy - matches billing cycle!")
    elif 80 <= accuracy <= 120:
        print("✅ Good accuracy - close to actual billing")
    else:
        print("⚠️ Still inaccurate - may need different approach")
    
    print(f"\n=== POST-RECHARGE COSTS ===")
    print(f"After 11:23 AM: ${costs_after_recharge:.2f} ({messages_after} msgs)")
    print("(These costs will appear in tomorrow's billing)")

if __name__ == "__main__":
    analyze_costs_by_time_window()
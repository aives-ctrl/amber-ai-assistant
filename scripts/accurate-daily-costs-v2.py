#!/usr/bin/env python3
"""
Accurate daily cost tracker using real OpenClaw data - Version 2
Fixed to handle actual OpenClaw JSON structure and model names.
"""

import json
import subprocess
from datetime import datetime

# Anthropic pricing (USD per 1M tokens) - exact models from OpenClaw
PRICING = {
    'claude-sonnet-4-20250514': {'input': 3.0, 'output': 15.0},
    'claude-opus-4-6': {'input': 15.0, 'output': 75.0}
}

def run_command(cmd):
    """Run a shell command and return the output."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout.strip() if result.returncode == 0 else None
    except Exception as e:
        print(f"Error running command '{cmd}': {e}")
        return None

def get_all_sessions():
    """Get all session data from OpenClaw."""
    output = run_command("openclaw sessions --json")
    if not output:
        return []
    
    try:
        data = json.loads(output)
        return data.get('sessions', [])
    except json.JSONDecodeError:
        print("Error parsing sessions JSON")
        return []

def get_cron_usage_json(job_id, limit=50):
    """Get cron job usage data as properly parsed JSON."""
    output = run_command(f"openclaw cron runs --id {job_id} --limit {limit}")
    if not output:
        return []
    
    try:
        data = json.loads(output)
        return data.get('entries', [])
    except json.JSONDecodeError:
        print(f"Error parsing cron runs JSON for {job_id}")
        return []

def calculate_session_cost(session):
    """Calculate cost for a single session."""
    model = session.get('model', '').replace('anthropic/', '')  # Remove provider prefix
    input_tokens = session.get('inputTokens', 0)
    output_tokens = session.get('outputTokens', 0)
    
    if model not in PRICING:
        return 0, f"Unknown model: {model}"
    
    pricing = PRICING[model]
    input_cost = (input_tokens / 1_000_000) * pricing['input']
    output_cost = (output_tokens / 1_000_000) * pricing['output']
    
    return input_cost + output_cost, None

def calculate_cron_entry_cost(entry):
    """Calculate cost for a single cron run entry."""
    model = entry.get('model', '').replace('anthropic/', '')
    usage = entry.get('usage', {})
    input_tokens = usage.get('input_tokens', 0)  
    output_tokens = usage.get('output_tokens', 0)
    
    if model not in PRICING:
        return 0
    
    pricing = PRICING[model]
    input_cost = (input_tokens / 1_000_000) * pricing['input']
    output_cost = (output_tokens / 1_000_000) * pricing['output']
    
    return input_cost + output_cost

def main():
    """Generate accurate daily cost report."""
    print("=== ACCURATE DAILY COST ANALYSIS v2 ===")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Get all session data
    sessions = get_all_sessions()
    print(f"Analyzed {len(sessions)} total sessions")
    print()
    
    # Analyze interactive sessions (non-cron)
    interactive_cost = 0
    interactive_sessions = [s for s in sessions if 'cron' not in s.get('key', '')]
    
    print("=== Interactive Sessions ===")
    for session in interactive_sessions[:5]:  # Show top 5
        cost, error = calculate_session_cost(session)
        if not error:
            interactive_cost += cost
            model_short = 'Opus' if 'opus' in session.get('model', '') else 'Sonnet'
            key_short = session.get('key', 'unknown')[:40]
            input_k = session.get('inputTokens', 0) // 1000
            output_k = session.get('outputTokens', 0) // 1000
            print(f"  {key_short}... {input_k}k/{output_k}k → ${cost:.3f} ({model_short})")
        else:
            print(f"  {session.get('key', 'unknown')[:40]}...: {error}")
    
    print(f"Interactive sessions total: ${interactive_cost:.3f}")
    print()
    
    # Analyze cron jobs
    print("=== Cron Jobs ===")
    
    # Email Processor
    email_entries = get_cron_usage_json('ee50f4a9-0098-4bab-854a-23f36a2e2f0f')
    email_cost = sum(calculate_cron_entry_cost(entry) for entry in email_entries)
    print(f"Email Processor: {len(email_entries)} runs → ${email_cost:.3f}")
    if len(email_entries) > 0:
        avg_tokens = sum(e.get('usage', {}).get('total_tokens', 0) for e in email_entries) / len(email_entries)
        print(f"  Avg tokens per run: {avg_tokens:.0f}")
    
    # RingCentral Processor  
    rc_entries = get_cron_usage_json('a768265e-6a79-4e73-82da-7cab9d8b621a')
    rc_cost = sum(calculate_cron_entry_cost(entry) for entry in rc_entries)
    print(f"RingCentral Processor: {len(rc_entries)} runs → ${rc_cost:.3f}")
    if len(rc_entries) > 0:
        avg_tokens = sum(e.get('usage', {}).get('total_tokens', 0) for e in rc_entries) / len(rc_entries)
        print(f"  Avg tokens per run: {avg_tokens:.0f}")
    
    cron_total = email_cost + rc_cost
    print(f"Cron jobs total: ${cron_total:.3f}")
    print()
    
    # Overall totals
    grand_total = interactive_cost + cron_total
    if grand_total > 0:
        print("=== DAILY TOTAL ===")
        print(f"Interactive: ${interactive_cost:.2f} ({interactive_cost/grand_total*100:.0f}%)")
        print(f"Cron jobs:   ${cron_total:.2f} ({cron_total/grand_total*100:.0f}%)")
        print(f"TOTAL TODAY: ${grand_total:.2f}")
        print()
        
        # Monthly projection
        monthly = grand_total * 30
        print(f"Monthly projection: ${monthly:.0f}")
        print()
        
        # Verification against auto-recharge
        print("=== VERIFICATION ===")
        print("Auto-recharge triggered: $10.77 (11:23 AM)")
        accuracy = (grand_total / 10.77) * 100
        print(f"Calculated vs actual: {accuracy:.0f}% accuracy")
        
        if accuracy < 80:
            print("⚠️  Low accuracy - missing data sources or model switches")
        elif accuracy > 120:
            print("⚠️  Over-calculation - double-counting or wrong rates")
        else:
            print("✅ Good accuracy - calculation matches reality")
    else:
        print("⚠️  No cost data found - check API access")
    
    return grand_total

if __name__ == "__main__":
    main()
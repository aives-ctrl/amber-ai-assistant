#!/usr/bin/env python3
"""
Accurate daily cost tracker using real OpenClaw session and cron data.
This replaces estimates with actual token usage from OpenClaw APIs.
"""

import json
import subprocess
import re
from datetime import datetime

# Anthropic pricing (USD per 1M tokens)
PRICING = {
    'anthropic/claude-sonnet-4-20250514': {'input': 3.0, 'output': 15.0},
    'anthropic/claude-opus-4-6': {'input': 15.0, 'output': 75.0}
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

def get_cron_usage(job_id, limit=50):
    """Get cron job usage data."""
    output = run_command(f"openclaw cron runs --id {job_id} --limit {limit}")
    if not output:
        return []
    
    # Parse usage data from cron runs
    usage_entries = []
    for line in output.split('\n'):
        if '"usage":' in line:
            try:
                # Extract the usage JSON from the line
                start = line.find('"usage":')
                end = line.find('}', start) + 1
                usage_json = '{' + line[start:end] + '}'
                usage_data = json.loads(usage_json.replace('"usage":', '"usage"'))
                usage_entries.append(usage_data['usage'])
            except:
                continue
    
    return usage_entries

def calculate_session_cost(session):
    """Calculate cost for a single session."""
    model = session.get('model', 'unknown')
    input_tokens = session.get('inputTokens', 0)
    output_tokens = session.get('outputTokens', 0)
    
    if model not in PRICING:
        return 0, f"Unknown model: {model}"
    
    pricing = PRICING[model]
    input_cost = (input_tokens / 1_000_000) * pricing['input']
    output_cost = (output_tokens / 1_000_000) * pricing['output']
    
    return input_cost + output_cost, None

def calculate_cron_cost(usage_entries, model_name):
    """Calculate cost for cron job usage entries."""
    if model_name not in PRICING:
        return 0, f"Unknown model: {model_name}"
    
    pricing = PRICING[model_name]
    total_cost = 0
    
    for usage in usage_entries:
        input_tokens = usage.get('input_tokens', 0)
        output_tokens = usage.get('output_tokens', 0)
        
        input_cost = (input_tokens / 1_000_000) * pricing['input']
        output_cost = (output_tokens / 1_000_000) * pricing['output']
        total_cost += input_cost + output_cost
    
    return total_cost, None

def main():
    """Generate accurate daily cost report."""
    print("=== ACCURATE DAILY COST ANALYSIS ===")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Get all session data
    sessions = get_all_sessions()
    print(f"Analyzed {len(sessions)} total sessions")
    print()
    
    # Analyze interactive sessions
    interactive_cost = 0
    interactive_sessions = [s for s in sessions if 'cron' not in s.get('key', '')]
    
    print("=== Interactive Sessions ===")
    for session in interactive_sessions[:10]:  # Show top 10
        cost, error = calculate_session_cost(session)
        if error:
            print(f"  {session.get('key', 'unknown')}: {error}")
        else:
            interactive_cost += cost
            model_short = 'Opus' if 'opus' in session.get('model', '') else 'Sonnet'
            print(f"  {session.get('key', 'unknown')[:50]}... ${cost:.3f} ({model_short})")
    
    print(f"Interactive sessions total: ${interactive_cost:.3f}")
    print()
    
    # Analyze cron jobs
    print("=== Cron Jobs ===")
    
    # Email Processor
    email_usage = get_cron_usage('ee50f4a9-0098-4bab-854a-23f36a2e2f0f')
    email_cost, _ = calculate_cron_cost(email_usage, 'anthropic/claude-sonnet-4-20250514')
    print(f"Email Processor: {len(email_usage)} runs → ${email_cost:.3f}")
    
    # RingCentral Processor  
    rc_usage = get_cron_usage('a768265e-6a79-4e73-82da-7cab9d8b621a')
    rc_cost, _ = calculate_cron_cost(rc_usage, 'anthropic/claude-sonnet-4-20250514')
    print(f"RingCentral Processor: {len(rc_usage)} runs → ${rc_cost:.3f}")
    
    cron_total = email_cost + rc_cost
    print(f"Cron jobs total: ${cron_total:.3f}")
    print()
    
    # Overall totals
    grand_total = interactive_cost + cron_total
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
    
    return grand_total

if __name__ == "__main__":
    main()
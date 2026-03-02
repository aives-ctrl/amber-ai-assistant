#!/usr/bin/env python3
"""
RingCentral Status Check - Show current monitoring status and recent activity
"""
import os
import json
import subprocess
from datetime import datetime, timezone

STATE_FILE = '/Users/amberives/.openclaw/workspace/ringcentral-state.json'

def load_state():
    """Load persistent state"""
    try:
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None

def check_launchd_status():
    """Check if the LaunchAgent is running"""
    try:
        result = subprocess.run(['launchctl', 'list', 'ai.openclaw.ringcentral.smart'], 
                              capture_output=True, text=True)
        return result.returncode == 0
    except:
        return False

def format_time_ago(iso_time):
    """Format time difference in human readable format"""
    try:
        time_obj = datetime.fromisoformat(iso_time.replace('Z', '+00:00'))
        now = datetime.now(timezone.utc)
        diff = now - time_obj
        
        if diff.days > 0:
            return f"{diff.days}d {diff.seconds//3600}h ago"
        elif diff.seconds > 3600:
            return f"{diff.seconds//3600}h {(diff.seconds%3600)//60}m ago"
        elif diff.seconds > 60:
            return f"{diff.seconds//60}m ago"
        else:
            return f"{diff.seconds}s ago"
    except:
        return "unknown"

def main():
    print("📱 RingCentral Monitoring Status")
    print("=" * 40)
    
    # Check LaunchAgent status
    is_running = check_launchd_status()
    status_icon = "✅" if is_running else "❌"
    print(f"{status_icon} Smart Polling Service: {'Running' if is_running else 'Not Running'}")
    
    # Load state information
    state = load_state()
    if state:
        print(f"📊 Total Messages Processed: {state.get('message_count', 0)}")
        print(f"🕐 Last Check: {format_time_ago(state.get('last_check', ''))}")
        
        errors = state.get('consecutive_errors', 0)
        error_icon = "✅" if errors == 0 else "⚠️" if errors < 3 else "❌"
        print(f"{error_icon} Consecutive Errors: {errors}")
        
        if state.get('last_message_id'):
            print(f"💬 Last Message ID: {state['last_message_id']}")
    else:
        print("⚠️ No state file found - service may not have run yet")
    
    # Check log file
    log_path = "/tmp/ringcentral-smart.log"
    if os.path.exists(log_path):
        try:
            stat = os.stat(log_path)
            size = stat.st_size
            modified = datetime.fromtimestamp(stat.st_mtime)
            print(f"📋 Log File: {size} bytes, modified {format_time_ago(modified.isoformat())}")
        except:
            print("📋 Log File: exists but unreadable")
    else:
        print("📋 Log File: not found")
    
    print()
    print("🔧 Management Commands:")
    print("  View logs: tail -f /tmp/ringcentral-smart.log")
    print("  Manual check: cd /Users/amberives/.openclaw/workspace && source sms-env/bin/activate && python scripts/ringcentral-smart-poll.py")
    print("  Stop service: launchctl unload ~/Library/LaunchAgents/ai.openclaw.ringcentral.smart.plist")
    print("  Start service: launchctl load ~/Library/LaunchAgents/ai.openclaw.ringcentral.smart.plist")

if __name__ == '__main__':
    main()
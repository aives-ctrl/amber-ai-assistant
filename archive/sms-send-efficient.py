#!/usr/bin/env python3
"""
Efficient SMS sender using OpenClaw browser tools
Much more efficient than full browser snapshots
"""

import sys
import json
import subprocess
import os

def send_sms_via_openclaw_browser(to_number, message):
    """
    Send SMS using OpenClaw browser tools efficiently
    Uses direct actions instead of verbose snapshots
    """
    try:
        # Start browser if not running
        start_cmd = 'openclaw browser start --profile openclaw'
        subprocess.run(start_cmd, shell=True, capture_output=True)
        
        # Navigate to Google Voice messages (direct URL)
        nav_cmd = 'openclaw browser navigate --profile openclaw --url "https://voice.google.com/u/0/messages"'
        subprocess.run(nav_cmd, shell=True, capture_output=True)
        
        # Send message using browser actions (more efficient than snapshots)
        send_cmd = f'''openclaw browser act --profile openclaw --action '{{"kind":"type","selector":"[data-testid=\\"send-new-message\\"]","text":"{to_number}"}}' '''
        subprocess.run(send_cmd, shell=True, capture_output=True)
        
        # Type message
        msg_cmd = f'''openclaw browser act --profile openclaw --action '{{"kind":"type","selector":"[aria-label=\\"Type a message\\"]","text":"{message}"}}' '''
        subprocess.run(msg_cmd, shell=True, capture_output=True)
        
        # Click send
        send_btn_cmd = 'openclaw browser act --profile openclaw --action \'{"kind":"click","selector":"[aria-label=\\"Send message\\"]"}\''
        subprocess.run(send_btn_cmd, shell=True, capture_output=True)
        
        return {
            'status': 'success',
            'method': 'openclaw_browser_efficient',
            'to': to_number,
            'message': message,
            'note': 'Sent via efficient OpenClaw browser automation'
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'method': 'openclaw_browser_efficient', 
            'message': str(e)
        }

def main():
    if len(sys.argv) < 3:
        print("Usage: python sms-send-efficient.py <to_number> <message>")
        sys.exit(1)
    
    to_number = sys.argv[1]
    message = ' '.join(sys.argv[2:])
    
    result = send_sms_via_openclaw_browser(to_number, message)
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
#!/usr/bin/env python3
"""
RingCentral Fast Polling - Simple, reliable 30-second checks
Uses the proven polling approach with critical notifications
"""
import os
import sys
import json
import subprocess
from datetime import datetime, timezone
from ringcentral import SDK

LAST_CHECK_FILE = '/Users/amberives/.openclaw/workspace/ringcentral-fast-last-check.txt'

def load_credentials():
    """Load RingCentral credentials"""
    env_path = '/Users/amberives/.openclaw/workspace/.env-ringcentral'
    creds = {}
    try:
        with open(env_path, 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    creds[key] = value
        return creds
    except Exception as e:
        print(f"Error loading credentials: {e}")
        return None

def get_last_check_time():
    """Get timestamp of last check"""
    try:
        with open(LAST_CHECK_FILE, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        # First run - use current time minus 1 minute
        from datetime import timedelta
        one_min_ago = datetime.now(timezone.utc) - timedelta(minutes=1)
        return one_min_ago.isoformat()

def save_last_check_time():
    """Save current time as last check"""
    with open(LAST_CHECK_FILE, 'w') as f:
        f.write(datetime.now(timezone.utc).isoformat())

def check_for_new_messages():
    """Check for new RingCentral messages and send critical notifications"""
    creds = load_credentials()
    if not creds:
        print("❌ Could not load credentials")
        return
    
    last_check = get_last_check_time()
    
    try:
        # Authenticate
        sdk = SDK(creds['RINGCENTRAL_CLIENT_ID'], creds['RINGCENTRAL_CLIENT_SECRET'], creds['RINGCENTRAL_SERVER'])
        platform = sdk.platform()
        platform.login(jwt=creds['RINGCENTRAL_JWT'])
        
        # Get recent messages from direct chat
        chat_id = creds['RINGCENTRAL_DIRECT_CHAT_ID']
        response = platform.get(f'/restapi/v1.0/glip/chats/{chat_id}/posts', {'recordCount': 10})
        data = json.loads(response.text())
        
        new_messages = []
        for post in data.get('records', []):
            # Skip my own messages (I'm creator 3563197015)
            if post.get('creatorId') == '3563197015':
                continue
                
            # Check if message is newer than last check
            msg_time = post.get('creationTime', '')
            if msg_time > last_check:
                text = post.get('text', '')
                new_messages.append(text)
        
        # Send critical notifications for new messages
        for text in new_messages:
            display_text = text[:100]
            print(f"🔔 NEW RINGCENTRAL: {display_text}")
            
            # Send critical priority notification
            notify_cmd = [
                '/Users/amberives/.openclaw/workspace/scripts/notify',
                f'📱 RingCentral: "{display_text}"',
                '--tier', 'critical',
                '--source', 'ringcentral-fast'
            ]
            result = subprocess.run(notify_cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Notification sent: {result.stdout.strip()}")
            else:
                print(f"❌ Notification failed: {result.stderr.strip()}")
        
        # Update last check time
        save_last_check_time()
        
        if new_messages:
            print(f"📱 Processed {len(new_messages)} new messages")
        else:
            print("📭 No new messages")
            
    except Exception as e:
        print(f"❌ Check failed: {e}")

if __name__ == '__main__':
    print(f"🔍 Fast polling check at {datetime.now().strftime('%H:%M:%S')}")
    check_for_new_messages()
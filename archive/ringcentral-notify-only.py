#!/usr/bin/env python3
"""
RingCentral Notifications Only - Clean, simple message detection
Just sends notifications when Dave messages me - no auto-responses
"""
import os
import sys
import json
import subprocess
from datetime import datetime, timezone
from ringcentral import SDK

LAST_MESSAGE_FILE = '/Users/amberives/.openclaw/workspace/ringcentral-last-message-id-notify.txt'

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

def get_last_message_id():
    """Get ID of last processed message"""
    try:
        with open(LAST_MESSAGE_FILE, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return None

def save_last_message_id(message_id):
    """Save ID of last processed message"""
    with open(LAST_MESSAGE_FILE, 'w') as f:
        f.write(str(message_id))

def send_notification(text):
    """Send critical notification"""
    try:
        notify_cmd = [
            '/Users/amberives/.openclaw/workspace/scripts/notify',
            f'📱 RingCentral: "{text[:100]}"',
            '--tier', 'critical',
            '--source', 'ringcentral-notify'
        ]
        result = subprocess.run(notify_cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Notification sent: {result.stdout.strip()}")
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Notification error: {e}")
        return False

def check_for_messages():
    """Check for new RingCentral messages and send notifications only"""
    creds = load_credentials()
    if not creds:
        return
    
    last_message_id = get_last_message_id()
    
    try:
        # Authenticate
        sdk = SDK(creds['RINGCENTRAL_CLIENT_ID'], creds['RINGCENTRAL_CLIENT_SECRET'], creds['RINGCENTRAL_SERVER'])
        platform = sdk.platform()
        platform.login(jwt=creds['RINGCENTRAL_JWT'])
        
        # Get recent messages
        chat_id = creds['RINGCENTRAL_DIRECT_CHAT_ID']
        response = platform.get(f'/restapi/v1.0/glip/chats/{chat_id}/posts', {'recordCount': 10})
        data = json.loads(response.text())
        
        new_messages = []
        latest_message_id = last_message_id
        
        for post in data.get('records', []):
            message_id = post.get('id')
            sender = post.get('creatorId')
            text = post.get('text', '')
            
            # Skip my own messages (I'm creator 3563197015)
            if sender == '3563197015':
                continue
            
            # Check if this is a new message
            if not last_message_id or str(message_id) > str(last_message_id):
                new_messages.append({
                    'id': message_id,
                    'text': text
                })
                
                if not latest_message_id or str(message_id) > str(latest_message_id):
                    latest_message_id = message_id
        
        # Send notifications for new messages
        for msg in new_messages:
            text = msg['text']
            print(f"🔔 NEW RINGCENTRAL MESSAGE: {text}")
            send_notification(text)
        
        # Update last message ID
        if latest_message_id and latest_message_id != last_message_id:
            save_last_message_id(latest_message_id)
        
        if new_messages:
            print(f"📱 Sent notifications for {len(new_messages)} new messages")
        else:
            print("📭 No new messages")
            
    except Exception as e:
        print(f"❌ Check failed: {e}")

if __name__ == '__main__':
    print(f"🔔 Notification check at {datetime.now().strftime('%H:%M:%S')}")
    check_for_messages()
#!/usr/bin/env python3
"""
RingCentral Bridge - Routes messages between RingCentral and main OpenClaw session
Simple approach: send RingCentral messages to main conversation, capture responses
"""
import os
import sys
import json
import subprocess
from datetime import datetime, timezone
from ringcentral import SDK

LAST_MESSAGE_FILE = '/Users/amberives/.openclaw/workspace/ringcentral-last-message-id.txt'

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
            '--source', 'ringcentral-bridge'
        ]
        subprocess.run(notify_cmd, capture_output=True, text=True)
    except Exception as e:
        print(f"❌ Notification error: {e}")

def send_to_main_conversation(message_text):
    """Send RingCentral message to main Telegram conversation"""
    try:
        # Use the message tool to send to this Telegram session
        msg_cmd = [
            'python', '-c', f'''
import sys
sys.path.append("/usr/local/lib/node_modules/openclaw/lib")
from openclaw.tools import message_tool

# Send the RingCentral message as if it came through Telegram  
result = message_tool.handle({{
    "action": "send",
    "message": "[RingCentral] {message_text.replace('"', '\\"')}",
    "channel": "telegram",
    "target": "8703088279"
}})
print("Message routed successfully")
'''
        ]
        
        result = subprocess.run(msg_cmd, capture_output=True, text=True, cwd='/Users/amberives/.openclaw/workspace')
        
        if result.returncode == 0:
            print(f"✅ Routed to main conversation: '{message_text}'")
            return True
        else:
            print(f"❌ Failed to route: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Routing error: {e}")
        return False

def check_and_forward():
    """Check for new RingCentral messages and forward to main conversation"""
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
            
            # Skip my own messages
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
        
        # Process new messages
        for msg in new_messages:
            text = msg['text']
            print(f"🔔 NEW RINGCENTRAL: {text}")
            
            # Send notification
            send_notification(text)
            
            # Route to main conversation
            send_to_main_conversation(text)
        
        # Update last message ID
        if latest_message_id and latest_message_id != last_message_id:
            save_last_message_id(latest_message_id)
        
        if new_messages:
            print(f"📱 Forwarded {len(new_messages)} messages to main conversation")
        else:
            print("📭 No new messages")
            
    except Exception as e:
        print(f"❌ Check failed: {e}")

if __name__ == '__main__':
    print(f"🌉 RingCentral bridge check at {datetime.now().strftime('%H:%M:%S')}")
    check_and_forward()
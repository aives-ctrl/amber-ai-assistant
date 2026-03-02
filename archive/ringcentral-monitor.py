#!/usr/bin/env python3
"""
RingCentral Message Monitor - Polls every 10 minutes for new messages
Fallback while WebSocket permissions are being resolved
"""
import os
import sys
import json
import time
import subprocess
from datetime import datetime, timezone
from ringcentral import SDK

LAST_CHECK_FILE = '/Users/amberives/.openclaw/workspace/ringcentral-last-check.txt'

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
        # First run - use current time minus 1 hour
        return datetime.now(timezone.utc).isoformat()

def save_last_check_time():
    """Save current time as last check"""
    with open(LAST_CHECK_FILE, 'w') as f:
        f.write(datetime.now(timezone.utc).isoformat())

def check_new_messages():
    """Check for new messages since last check"""
    creds = load_credentials()
    if not creds:
        return {'status': 'error', 'message': 'Could not load credentials'}
    
    last_check = get_last_check_time()
    
    try:
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
                new_messages.append({
                    'from': post.get('creatorId'),
                    'text': post.get('text', ''),
                    'time': msg_time,
                    'id': post.get('id')
                })
        
        # Notify about new messages
        for msg in new_messages:
            text = msg['text'][:100]
            print(f"📱 NEW: {text}")
            
            # Send to notification queue
            notify_cmd = [
                '/Users/amberives/.openclaw/workspace/scripts/notify',
                f'📱 RingCentral: "{text}"',
                '--tier', 'high',
                '--source', 'ringcentral-poll'
            ]
            subprocess.run(notify_cmd, capture_output=True)
        
        # Update last check time
        save_last_check_time()
        
        return {
            'status': 'success',
            'new_messages': len(new_messages),
            'messages': new_messages
        }
        
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

if __name__ == '__main__':
    result = check_new_messages()
    if result['status'] == 'success':
        count = result['new_messages']
        if count > 0:
            print(f"📱 Found {count} new RingCentral messages")
        else:
            print("📱 No new RingCentral messages")
    else:
        print(f"❌ RingCentral check failed: {result['message']}")
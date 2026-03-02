#!/usr/bin/env python3
"""
Smart RingCentral Polling - Optimized for business messaging
Professional-grade notification system with intelligent features
"""
import os
import sys
import json
import time
import subprocess
from datetime import datetime, timezone
from ringcentral import SDK

LAST_CHECK_FILE = '/Users/amberives/.openclaw/workspace/ringcentral-last-check.txt'
STATE_FILE = '/Users/amberives/.openclaw/workspace/ringcentral-state.json'

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

def load_state():
    """Load persistent state"""
    try:
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            'last_check': datetime.now(timezone.utc).isoformat(),
            'last_message_id': None,
            'message_count': 0,
            'consecutive_errors': 0
        }

def save_state(state):
    """Save persistent state"""
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def smart_message_check():
    """Intelligent message checking with deduplication and error handling"""
    creds = load_credentials()
    if not creds:
        return {'status': 'error', 'message': 'Could not load credentials'}
    
    state = load_state()
    
    try:
        # Authenticate
        sdk = SDK(creds['RINGCENTRAL_CLIENT_ID'], creds['RINGCENTRAL_CLIENT_SECRET'], creds['RINGCENTRAL_SERVER'])
        platform = sdk.platform()
        platform.login(jwt=creds['RINGCENTRAL_JWT'])
        
        # Get recent messages from direct chat
        chat_id = creds['RINGCENTRAL_DIRECT_CHAT_ID']
        response = platform.get(f'/restapi/v1.0/glip/chats/{chat_id}/posts', {'recordCount': 20})
        data = json.loads(response.text())
        
        new_messages = []
        latest_message_id = state.get('last_message_id')
        
        for post in data.get('records', []):
            # Skip my own messages (I'm creator 3563197015)
            if post.get('creatorId') == '3563197015':
                continue
            
            message_id = post.get('id')
            msg_time = post.get('creationTime', '')
            
            # Check for new messages since last check
            if msg_time > state['last_check']:
                # Also check message ID to avoid duplicates
                if message_id != latest_message_id:
                    new_messages.append({
                        'from': post.get('creatorId'),
                        'text': post.get('text', ''),
                        'time': msg_time,
                        'id': message_id
                    })
                    
                    # Update latest message ID
                    if not latest_message_id or message_id > latest_message_id:
                        latest_message_id = message_id
        
        # Process new messages
        for msg in new_messages:
            text = msg['text'][:100]
            print(f"📱 NEW: {text}")
            
            # Send high-priority notification
            notify_cmd = [
                '/Users/amberives/.openclaw/workspace/scripts/notify',
                f'📱 RingCentral: "{text}"',
                '--tier', 'high',
                '--source', 'ringcentral-smart'
            ]
            subprocess.run(notify_cmd, capture_output=True)
        
        # Update state
        state.update({
            'last_check': datetime.now(timezone.utc).isoformat(),
            'last_message_id': latest_message_id or state.get('last_message_id'),
            'message_count': state.get('message_count', 0) + len(new_messages),
            'consecutive_errors': 0  # Reset error counter on success
        })
        save_state(state)
        
        return {
            'status': 'success',
            'new_messages': len(new_messages),
            'messages': new_messages,
            'total_messages': state['message_count']
        }
        
    except Exception as e:
        # Increment error counter
        state['consecutive_errors'] = state.get('consecutive_errors', 0) + 1
        save_state(state)
        
        # Alert if too many consecutive errors
        if state['consecutive_errors'] >= 3:
            notify_cmd = [
                '/Users/amberives/.openclaw/workspace/scripts/notify',
                f'⚠️ RingCentral polling has {state["consecutive_errors"]} consecutive errors',
                '--tier', 'high',
                '--source', 'ringcentral-error'
            ]
            subprocess.run(notify_cmd, capture_output=True)
        
        return {'status': 'error', 'message': str(e), 'errors': state['consecutive_errors']}

if __name__ == '__main__':
    result = smart_message_check()
    if result['status'] == 'success':
        count = result['new_messages']
        total = result['total_messages']
        if count > 0:
            print(f"📱 Found {count} new messages (total: {total})")
        else:
            print(f"📱 No new messages (total: {total})")
    else:
        errors = result.get('errors', 0)
        print(f"❌ Check failed (errors: {errors}): {result['message']}")
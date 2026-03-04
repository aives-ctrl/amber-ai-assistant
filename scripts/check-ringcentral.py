#!/usr/bin/env python3
"""
Check RingCentral for new messages - ultra-efficient heartbeat integration
"""
import os
import sys
import json
from datetime import datetime
from ringcentral import SDK

def load_credentials():
    """Load RingCentral credentials from .env file"""
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

def check_messages():
    """Check for new RingCentral messages"""
    creds = load_credentials()
    if not creds:
        return {'status': 'error', 'message': 'Could not load credentials'}
    
    try:
        sdk = SDK(creds['RINGCENTRAL_CLIENT_ID'], creds['RINGCENTRAL_CLIENT_SECRET'], creds['RINGCENTRAL_SERVER'])
        platform = sdk.platform()
        platform.login(jwt=creds['RINGCENTRAL_JWT'])
        
        # Check direct chat with Dave
        chat_id = creds['RINGCENTRAL_DIRECT_CHAT_ID']
        response = platform.get(f'/restapi/v1.0/glip/chats/{chat_id}/posts', {'recordCount': 5})
        data = json.loads(response.text())
        
        messages = []
        for post in data.get('records', []):
            # Skip my own messages (I'm creator 3563197015 based on JWT)
            if post.get('creatorId') != '3563197015':
                messages.append({
                    'from': post.get('creatorId'),
                    'text': post.get('text', ''),
                    'time': post.get('creationTime'),
                    'id': post.get('id')
                })
        
        return {
            'status': 'success',
            'new_messages': len(messages),
            'messages': messages[:3]  # Return last 3 messages
        }
        
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

if __name__ == '__main__':
    result = check_messages()
    if len(sys.argv) > 1 and sys.argv[1] == '--json':
        print(json.dumps(result, indent=2))
    else:
        if result['status'] == 'success':
            new_count = result['new_messages']
            if new_count > 0:
                print(f"📱 {new_count} recent RingCentral messages")
                for msg in result['messages']:
                    print(f"  {msg['time']}: {msg['text'][:100]}")
            else:
                print("📱 No new RingCentral messages")
        else:
            print(f"❌ RingCentral check failed: {result['message']}")
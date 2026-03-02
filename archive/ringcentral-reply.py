#!/usr/bin/env python3
"""
Simple RingCentral Reply Tool
Usage: python ringcentral-reply.py "Your message here"
"""
import sys
import json
from ringcentral import SDK

def send_ringcentral_message(message_text):
    """Send a message to RingCentral direct chat"""
    # Load credentials
    creds = {}
    env_path = '/Users/amberives/.openclaw/workspace/.env-ringcentral'
    try:
        with open(env_path, 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    creds[key] = value
    except Exception as e:
        print(f"❌ Error loading credentials: {e}")
        return False
    
    try:
        # Authenticate
        sdk = SDK(creds['RINGCENTRAL_CLIENT_ID'], creds['RINGCENTRAL_CLIENT_SECRET'], creds['RINGCENTRAL_SERVER'])
        platform = sdk.platform()
        platform.login(jwt=creds['RINGCENTRAL_JWT'])
        
        # Send message
        chat_id = creds['RINGCENTRAL_DIRECT_CHAT_ID']
        response = platform.post(f'/restapi/v1.0/glip/chats/{chat_id}/posts', {
            'text': message_text
        })
        
        print(f"✅ Message sent to RingCentral: '{message_text}'")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send message: {e}")
        return False

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python ringcentral-reply.py 'Your message here'")
        sys.exit(1)
    
    message = ' '.join(sys.argv[1:])
    send_ringcentral_message(message)
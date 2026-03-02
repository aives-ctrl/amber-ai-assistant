#!/usr/bin/env python3
"""
RingCentral Team Messaging - Check internal messages/chats
This is different from SMS - it's the team chat feature within RingCentral
"""

import os
import json
import sys
from ringcentral import SDK

# RingCentral configuration - need credentials from Dave
RINGCENTRAL_CLIENT_ID = os.getenv('RINGCENTRAL_CLIENT_ID', 'YOUR_CLIENT_ID')
RINGCENTRAL_CLIENT_SECRET = os.getenv('RINGCENTRAL_CLIENT_SECRET', 'YOUR_CLIENT_SECRET') 
RINGCENTRAL_SERVER = os.getenv('RINGCENTRAL_SERVER', 'https://platform.ringcentral.com')
RINGCENTRAL_USERNAME = os.getenv('RINGCENTRAL_USERNAME', 'YOUR_USERNAME')
RINGCENTRAL_EXTENSION = os.getenv('RINGCENTRAL_EXTENSION', 'YOUR_EXTENSION')
RINGCENTRAL_PASSWORD = os.getenv('RINGCENTRAL_PASSWORD', 'YOUR_PASSWORD')

def authenticate_ringcentral():
    """Authenticate with RingCentral"""
    try:
        sdk = SDK(RINGCENTRAL_CLIENT_ID, RINGCENTRAL_CLIENT_SECRET, RINGCENTRAL_SERVER)
        platform = sdk.platform()
        platform.login(RINGCENTRAL_USERNAME, RINGCENTRAL_EXTENSION, RINGCENTRAL_PASSWORD)
        print("✅ RingCentral authentication successful!")
        return platform
    except Exception as e:
        print(f"❌ RingCentral authentication failed: {e}")
        return None

def get_team_messages(platform):
    """Get recent team chat messages"""
    try:
        # Try different endpoints for team messaging
        endpoints_to_try = [
            '/restapi/v1.0/glip/posts',  # Glip is RingCentral's team messaging
            '/restapi/v1.0/glip/chats',
            '/restapi/v1.0/glip/conversations', 
            '/restapi/v1.0/account/~/extension/~/message-store'
        ]
        
        for endpoint in endpoints_to_try:
            try:
                print(f"Trying endpoint: {endpoint}")
                response = platform.get(endpoint, {'recordCount': 10})
                data = response.json()
                print(f"✅ {endpoint} - Success!")
                print(json.dumps(data, indent=2)[:500] + "...")
                return data
            except Exception as e:
                print(f"❌ {endpoint} - Failed: {e}")
                continue
        
        return {'status': 'error', 'message': 'No working endpoints found'}
        
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

def send_team_message(platform, message, chat_id=None):
    """Send a team chat message"""
    try:
        # Try to send to team chat
        if chat_id:
            response = platform.post(f'/restapi/v1.0/glip/chats/{chat_id}/posts', {
                'text': message
            })
        else:
            # Try to find a chat first
            chats_response = platform.get('/restapi/v1.0/glip/chats')
            chats = chats_response.json()
            if chats.get('records'):
                chat_id = chats['records'][0]['id']
                response = platform.post(f'/restapi/v1.0/glip/chats/{chat_id}/posts', {
                    'text': message
                })
            else:
                return {'status': 'error', 'message': 'No chats found'}
        
        result = response.json()
        return {
            'status': 'success',
            'method': 'ringcentral_team_chat',
            'message': message,
            'chat_id': chat_id,
            'result': result
        }
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

def main():
    """CLI interface for RingCentral team messaging"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python ringcentral-team-chat.py check                    # Check for team messages")
        print("  python ringcentral-team-chat.py send <message>           # Send team message")
        sys.exit(1)
    
    # Authenticate first
    platform = authenticate_ringcentral()
    if not platform:
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == 'check':
        result = get_team_messages(platform)
    elif action == 'send' and len(sys.argv) >= 3:
        message = ' '.join(sys.argv[2:])
        result = send_team_message(platform, message)
    else:
        print("Invalid arguments")
        sys.exit(1)
    
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
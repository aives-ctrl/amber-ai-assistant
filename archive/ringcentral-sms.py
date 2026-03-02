#!/usr/bin/env python3
"""
RingCentral SMS Integration - Much more reliable than Google Voice!
Official API with proper authentication and documentation.
"""

import os
import json
import sys
from ringcentral import SDK

# RingCentral configuration (will need these from Dave)
RINGCENTRAL_CLIENT_ID = os.getenv('RINGCENTRAL_CLIENT_ID', 'YOUR_CLIENT_ID')
RINGCENTRAL_CLIENT_SECRET = os.getenv('RINGCENTRAL_CLIENT_SECRET', 'YOUR_CLIENT_SECRET') 
RINGCENTRAL_SERVER = os.getenv('RINGCENTRAL_SERVER', 'https://platform.ringcentral.com')  # or https://platform.devtest.ringcentral.com for sandbox
RINGCENTRAL_USERNAME = os.getenv('RINGCENTRAL_USERNAME', 'YOUR_USERNAME')
RINGCENTRAL_EXTENSION = os.getenv('RINGCENTRAL_EXTENSION', 'YOUR_EXTENSION')
RINGCENTRAL_PASSWORD = os.getenv('RINGCENTRAL_PASSWORD', 'YOUR_PASSWORD')

def authenticate_ringcentral():
    """Authenticate with RingCentral - much more reliable than Google Voice"""
    try:
        sdk = SDK(RINGCENTRAL_CLIENT_ID, RINGCENTRAL_CLIENT_SECRET, RINGCENTRAL_SERVER)
        platform = sdk.platform()
        platform.login(RINGCENTRAL_USERNAME, RINGCENTRAL_EXTENSION, RINGCENTRAL_PASSWORD)
        
        print("✅ RingCentral authentication successful!")
        return platform
    except Exception as e:
        print(f"❌ RingCentral authentication failed: {e}")
        return None

def send_sms(platform, to_number, message):
    """Send SMS via RingCentral - super efficient!"""
    try:
        # Send SMS using RingCentral API
        response = platform.post('/restapi/v1.0/account/~/extension/~/sms', {
            'to': [{'phoneNumber': to_number}],
            'text': message
        })
        
        result = response.json()
        print(f"✅ SMS sent successfully!")
        return {
            'status': 'success',
            'method': 'ringcentral_api',
            'to': to_number,
            'message': message,
            'message_id': result.get('id'),
            'cost': 'Minimal API tokens vs browser automation'
        }
    except Exception as e:
        return {
            'status': 'error', 
            'method': 'ringcentral_api',
            'message': str(e)
        }

def get_sms_messages(platform):
    """Get recent SMS messages - very efficient"""
    try:
        response = platform.get('/restapi/v1.0/account/~/extension/~/message-store', {
            'messageType': 'SMS',
            'readStatus': 'Unread',
            'perPage': 10
        })
        
        messages = response.json()
        result = []
        
        for msg in messages.get('records', []):
            result.append({
                'id': msg.get('id'),
                'from': msg.get('from', {}).get('phoneNumber'),
                'text': msg.get('subject'),  # SMS text is in subject field
                'time': msg.get('creationTime'),
                'direction': msg.get('direction')
            })
            
        return {'status': 'success', 'messages': result}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

def main():
    """CLI interface for RingCentral SMS"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python ringcentral-sms.py check                    # Check for new messages")
        print("  python ringcentral-sms.py send <number> <message>  # Send SMS")
        sys.exit(1)
    
    # Authenticate first
    platform = authenticate_ringcentral()
    if not platform:
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == 'check':
        result = get_sms_messages(platform)
    elif action == 'send' and len(sys.argv) >= 4:
        to_number = sys.argv[2]
        message = ' '.join(sys.argv[3:])
        result = send_sms(platform, to_number, message)
    else:
        print("Invalid arguments")
        sys.exit(1)
    
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
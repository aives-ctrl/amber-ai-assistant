#!/usr/bin/env python3
"""
Efficient SMS handling via Google Voice Python library
Much more token-efficient than browser automation
"""

import sys
import json
from datetime import datetime
from googlevoice import Voice

def authenticate():
    """Authenticate with Google Voice - will need credentials"""
    voice = Voice()
    # voice.login(email, password)  # Will need to configure this
    return voice

def check_messages():
    """Check for new SMS messages - very token efficient"""
    try:
        voice = authenticate()
        voice.sms()
        messages = []
        
        for msg in voice.sms.html:
            # Extract message details efficiently
            messages.append({
                'from': msg.phoneNumber,
                'text': msg.messageText,
                'time': msg.time,
                'id': msg.id
            })
            
        return {'status': 'success', 'messages': messages}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

def send_message(to, text):
    """Send SMS message - much faster than browser"""
    try:
        voice = authenticate()
        voice.send_sms(to, text)
        return {'status': 'success', 'to': to, 'text': text}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

def main():
    """CLI interface"""
    if len(sys.argv) < 2:
        print("Usage: python sms.py check|send <to> <message>")
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == 'check':
        result = check_messages()
    elif action == 'send' and len(sys.argv) >= 4:
        to = sys.argv[2]
        message = ' '.join(sys.argv[3:])
        result = send_message(to, message)
    else:
        print("Invalid arguments")
        sys.exit(1)
    
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
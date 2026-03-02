#!/usr/bin/env python3
"""
RingCentral Responsive System - Detects messages and responds automatically
Proper message detection using message IDs + automatic responses
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
            '--source', 'ringcentral-responsive'
        ]
        result = subprocess.run(notify_cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Notification sent: {result.stdout.strip()}")
        else:
            print(f"❌ Notification failed: {result.stderr.strip()}")
    except Exception as e:
        print(f"❌ Notification error: {e}")

def create_ringcentral_response(original_text):
    """Use OpenClaw sub-agent to generate natural response"""
    try:
        # Create a sub-agent session specifically for RingCentral conversations
        spawn_cmd = [
            'openclaw', 'sessions', 'spawn',
            '--runtime', 'subagent', 
            '--mode', 'run',
            '--task', f'Dave sent this message in RingCentral: "{original_text}". Respond naturally as Amber, his AI assistant, the same way you would in any other chat. Keep it conversational and helpful. This is just like our normal conversation, but happening in RingCentral instead of Telegram.',
            '--model', 'anthropic/claude-sonnet-4-20250514',
            '--timeout-seconds', '30'
        ]
        
        result = subprocess.run(spawn_cmd, capture_output=True, text=True, cwd='/Users/amberives/.openclaw/workspace')
        
        if result.returncode == 0:
            # Extract the response from the sub-agent output
            response_text = result.stdout.strip()
            # Clean up any system messages or formatting
            if "Task completed successfully" in response_text:
                lines = response_text.split('\n')
                for line in lines:
                    if line.strip() and not line.startswith('[') and not 'Task completed' in line:
                        return line.strip()
            else:
                return response_text[:500]  # Limit length
        else:
            print(f"❌ Sub-agent failed: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Sub-agent error: {e}")
        return None

def send_response(platform, chat_id, original_text):
    """Generate and send natural AI response using sub-agent"""
    try:
        # Skip very short fragments
        if len(original_text.strip()) <= 2:
            print(f"📭 Skipping fragment: '{original_text}'")
            return True
        
        print(f"🤖 Generating natural response for: '{original_text}'")
        
        # Get AI-generated response
        ai_response = create_ringcentral_response(original_text)
        
        if ai_response:
            response_text = ai_response
        else:
            # Fallback if AI response fails
            response_text = "I'm here! The AI response system had a hiccup, but I got your message."
        
        # Send to RingCentral
        response = platform.post(f'/restapi/v1.0/glip/chats/{chat_id}/posts', {
            'text': response_text
        })
        
        print(f"✅ AI response sent: '{response_text[:50]}{'...' if len(response_text) > 50 else ''}'")
        return True
        
    except Exception as e:
        print(f"❌ Response failed: {e}")
        return False

def check_and_respond():
    """Check for new messages and respond automatically"""
    creds = load_credentials()
    if not creds:
        print("❌ Could not load credentials")
        return
    
    last_message_id = get_last_message_id()
    
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
        latest_message_id = last_message_id
        
        for post in data.get('records', []):
            message_id = post.get('id')
            sender = post.get('creatorId')
            text = post.get('text', '')
            
            # Skip my own messages (I'm creator 3563197015)
            if sender == '3563197015':
                continue
            
            # Check if this is a new message (message ID is greater than last processed)
            if not last_message_id or str(message_id) > str(last_message_id):
                new_messages.append({
                    'id': message_id,
                    'text': text,
                    'sender': sender
                })
                
                # Update latest message ID
                if not latest_message_id or str(message_id) > str(latest_message_id):
                    latest_message_id = message_id
        
        # Process new messages from Dave
        for msg in new_messages:
            text = msg['text']
            print(f"🔔 NEW MESSAGE: {text}")
            
            # Send notification
            send_notification(text)
            
            # Send automatic response
            send_response(platform, chat_id, text)
        
        # Update last processed message ID
        if latest_message_id and latest_message_id != last_message_id:
            save_last_message_id(latest_message_id)
            print(f"📝 Updated last message ID: {latest_message_id}")
        
        if new_messages:
            print(f"📱 Processed {len(new_messages)} new messages")
        else:
            print("📭 No new messages")
            
    except Exception as e:
        print(f"❌ Check failed: {e}")

if __name__ == '__main__':
    print(f"🔍 Responsive check at {datetime.now().strftime('%H:%M:%S')}")
    check_and_respond()
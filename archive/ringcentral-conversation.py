#!/usr/bin/env python3
"""
RingCentral Conversation Handler
Natural conversations in RingCentral using OpenClaw AI sessions
"""
import os
import sys
import json
import subprocess
import tempfile
from datetime import datetime, timezone
from ringcentral import SDK

LAST_MESSAGE_FILE = '/Users/amberives/.openclaw/workspace/ringcentral-conversation-last-id.txt'

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
        print(f"❌ Error loading credentials: {e}")
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

def generate_ai_response(message_text):
    """Generate AI response using OpenClaw CLI"""
    try:
        # Create the task for the AI
        task = f'''Dave sent you this message in RingCentral: "{message_text}"

Respond naturally as Amber, his AI assistant. You're the same Amber from all his other conversations - professional but warm, concise, and helpful. This is just RingCentral instead of Telegram.

Key context:
- You're Amber Ives, AI chief of staff at MindFire  
- Dave is president of MindFire
- Be direct and skip filler words
- Keep it conversational and useful'''

        print("🤖 Generating AI response with OpenClaw...")
        
        # Use OpenClaw CLI to spawn a sub-agent with full paths
        env = os.environ.copy()
        env['PATH'] = '/usr/local/bin:/usr/bin:/bin'  # Ensure node is in PATH
        
        result = subprocess.run([
            '/usr/local/bin/node', '/usr/local/bin/openclaw', 'sessions', 'spawn',
            '--task', task,
            '--mode', 'run',
            '--model', 'anthropic/claude-sonnet-4-20250514',
            '--timeout-seconds', '30'
        ], capture_output=True, text=True, cwd='/Users/amberives/.openclaw/workspace', env=env)
        
        if result.returncode == 0:
            response_text = result.stdout.strip()
            
            # Extract the actual response from OpenClaw output
            lines = response_text.split('\n')
            response_lines = []
            
            for line in lines:
                line = line.strip()
                # Skip system messages, prompts, and formatting
                if (line and 
                    not line.startswith('🦞') and
                    not line.startswith('🕒') and  
                    not line.startswith('🧠') and
                    not line.startswith('🧮') and
                    not line.startswith('📚') and
                    not line.startswith('🧵') and
                    not line.startswith('⚙️') and
                    not line.startswith('[') and
                    not line.startswith('Task completed') and
                    not line.startswith('Session completed') and
                    not 'spawn' in line.lower() and
                    len(line) > 10):  # Ignore very short lines
                    response_lines.append(line)
            
            if response_lines:
                # Take the best response line (usually the longest meaningful one)
                best_response = max(response_lines, key=len)[:400]  # Limit length
                print(f"✅ AI response: '{best_response[:60]}...'")
                return best_response
            else:
                print("❌ No meaningful response found in output")
                return None
        else:
            print(f"❌ OpenClaw spawn failed: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"❌ AI response generation error: {e}")
        return None

def send_to_ringcentral(platform, chat_id, response_text):
    """Send response to RingCentral"""
    try:
        result = platform.post(f'/restapi/v1.0/glip/chats/{chat_id}/posts', {
            'text': response_text
        })
        print(f"✅ Response sent to RingCentral: '{response_text}'")
        return True
    except Exception as e:
        print(f"❌ Failed to send to RingCentral: {e}")
        return False

def process_ringcentral_conversations():
    """Main conversation processing loop"""
    creds = load_credentials()
    if not creds:
        print("❌ Could not load credentials")
        return
    
    last_message_id = get_last_message_id()
    
    try:
        # Authenticate with RingCentral
        sdk = SDK(creds['RINGCENTRAL_CLIENT_ID'], creds['RINGCENTRAL_CLIENT_SECRET'], creds['RINGCENTRAL_SERVER'])
        platform = sdk.platform()
        platform.login(jwt=creds['RINGCENTRAL_JWT'])
        
        # Get recent messages from direct chat
        chat_id = creds['RINGCENTRAL_DIRECT_CHAT_ID']
        response = platform.get(f'/restapi/v1.0/glip/chats/{chat_id}/posts', {'recordCount': 5})
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
        
        # Process each new message
        for msg in new_messages:
            text = msg['text']
            print(f"💬 NEW RINGCENTRAL MESSAGE: '{text}'")
            
            # Generate AI response
            ai_response = generate_ai_response(text)
            
            if ai_response:
                # Send response to RingCentral
                send_to_ringcentral(platform, chat_id, ai_response)
            else:
                # Fallback response if AI fails
                fallback = f"I received your message: '{text}' - but had trouble generating a response. The conversation system is still being refined."
                send_to_ringcentral(platform, chat_id, fallback)
        
        # Update last processed message ID
        if latest_message_id and latest_message_id != last_message_id:
            save_last_message_id(latest_message_id)
            print(f"📝 Updated last message ID: {latest_message_id}")
        
        if new_messages:
            print(f"💬 Processed {len(new_messages)} RingCentral conversations")
        else:
            print("📭 No new RingCentral messages")
            
    except Exception as e:
        print(f"❌ Conversation processing failed: {e}")

if __name__ == '__main__':
    print(f"💬 RingCentral conversation check at {datetime.now().strftime('%H:%M:%S')}")
    process_ringcentral_conversations()
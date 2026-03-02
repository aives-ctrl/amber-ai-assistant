#!/usr/bin/env python3 -u
"""
RingCentral Conversation Service v2
Real-time WebSocket + Anthropic AI for natural conversations
"""
import os
import sys
import json
import asyncio
import aiohttp
import signal
import subprocess
import functools
from datetime import datetime, timezone
from pathlib import Path

# Force unbuffered output
print = functools.partial(print, flush=True)

import anthropic
from ringcentral import SDK

# Paths
WORKSPACE = '/Users/amberives/.openclaw/workspace'
HISTORY_DIR = os.path.join(WORKSPACE, 'ringcentral-history')
ENV_FILE = os.path.join(WORKSPACE, '.env-ringcentral')
SOUL_FILE = os.path.join(WORKSPACE, 'SOUL.md')
USER_FILE = os.path.join(WORKSPACE, 'USER.md')
IDENTITY_FILE = os.path.join(WORKSPACE, 'IDENTITY.md')
RC_FILE = os.path.join(WORKSPACE, 'RINGCENTRAL.md')
MEMORY_FILE = os.path.join(WORKSPACE, 'MEMORY.md')

# My RingCentral user ID - skip my own messages
MY_USER_ID = '3563197015'

# Max conversation history per chat
MAX_HISTORY_MESSAGES = 40


def load_file(path):
    """Load a text file, return empty string if missing"""
    try:
        with open(path, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return ''


def load_credentials():
    """Load RingCentral credentials from env file"""
    creds = {}
    try:
        with open(ENV_FILE, 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    creds[key] = value
        return creds
    except Exception as e:
        print(f"❌ Error loading credentials: {e}")
        return None


def load_chat_history(chat_id):
    """Load conversation history for a specific chat"""
    history_file = os.path.join(HISTORY_DIR, f'{chat_id}.json')
    try:
        with open(history_file, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_chat_history(chat_id, history):
    """Save conversation history for a specific chat, keeping last N messages"""
    history_file = os.path.join(HISTORY_DIR, f'{chat_id}.json')
    # Trim to max history
    trimmed = history[-MAX_HISTORY_MESSAGES:]
    with open(history_file, 'w') as f:
        json.dump(trimmed, f, indent=2)


def build_system_prompt():
    """Build system prompt from persona files"""
    soul = load_file(SOUL_FILE)
    user = load_file(USER_FILE)
    identity = load_file(IDENTITY_FILE)
    rc_rules = load_file(RC_FILE)
    memory = load_file(MEMORY_FILE)

    return f"""You are Amber Ives, AI chief of staff and assistant to Dave Rosendahl at MindFire.

You are responding in RingCentral, which is the company's primary team messaging platform. Your whole team uses it. Behave like a real person on the team.

{identity}

{soul}

{user}

{rc_rules}

## Key Memory Context
{memory[:2000]}

## Important Notes
- You're on RingCentral right now. Respond naturally like a team member.
- Keep responses concise and conversational - this is chat, not email.
- In group chats, be aware everyone can see your messages.
- In 1-on-1 chats, only the other person sees your messages.
- You can take actions (schedule meetings, send emails, check things) - just mention what you'll do.
- If Dave asks for "big brain" or "Opus", acknowledge it (model switching is handled externally).
- Don't use markdown headers or heavy formatting - keep it chat-natural.
- No em dashes. Use commas, periods, or semicolons instead.
"""


def generate_response(message_text, chat_history, sender_name='Dave'):
    """Generate AI response using Anthropic API"""
    try:
        # Build messages from chat history
        messages = []
        for entry in chat_history:
            role = 'assistant' if entry.get('is_me') else 'user'
            content = entry.get('text', '')
            if content:
                # Add sender context for user messages
                if role == 'user' and entry.get('sender_name'):
                    content = f"[{entry['sender_name']}]: {content}"
                messages.append({'role': role, 'content': content})

        # Add the new message
        messages.append({
            'role': 'user',
            'content': f"[{sender_name}]: {message_text}" if sender_name else message_text
        })

        # Ensure messages alternate properly (Anthropic requirement)
        cleaned_messages = []
        last_role = None
        for msg in messages:
            if msg['role'] == last_role:
                # Merge consecutive same-role messages
                cleaned_messages[-1]['content'] += '\n' + msg['content']
            else:
                cleaned_messages.append(msg)
                last_role = msg['role']

        # Ensure first message is 'user'
        if cleaned_messages and cleaned_messages[0]['role'] != 'user':
            cleaned_messages = cleaned_messages[1:]

        if not cleaned_messages:
            cleaned_messages = [{'role': 'user', 'content': f"[{sender_name}]: {message_text}"}]

        # Call Anthropic API
        client = anthropic.Anthropic(
            api_key=os.environ.get('ANTHROPIC_API_KEY')
        )

        response = client.messages.create(
            model='claude-sonnet-4-20250514',
            max_tokens=500,
            system=build_system_prompt(),
            messages=cleaned_messages
        )

        return response.content[0].text

    except Exception as e:
        print(f"❌ AI response error: {e}")
        import traceback
        traceback.print_exc()
        return None


class RingCentralService:
    def __init__(self):
        self.running = False
        self.creds = load_credentials()
        self.platform = None
        self.sdk = None
        self.reconnect_delay = 5

    def authenticate(self):
        """Authenticate with RingCentral"""
        self.sdk = SDK(
            self.creds['RINGCENTRAL_CLIENT_ID'],
            self.creds['RINGCENTRAL_CLIENT_SECRET'],
            self.creds['RINGCENTRAL_SERVER']
        )
        self.platform = self.sdk.platform()
        self.platform.login(jwt=self.creds['RINGCENTRAL_JWT'])
        print("✅ RingCentral authenticated")

    def get_ws_credentials(self):
        """Get WebSocket credentials"""
        ws = self.sdk.create_web_socket_client()
        token_response = ws.get_web_socket_token()
        return {
            'uri': token_response['uri'],
            'token': token_response['ws_access_token'],
            'expires': token_response['expires_in']
        }

    def get_sender_name(self, creator_id):
        """Look up sender name from RingCentral"""
        try:
            response = self.platform.get(f'/restapi/v1.0/glip/persons/{creator_id}')
            data = json.loads(response.text())
            first = data.get('firstName', '')
            last = data.get('lastName', '')
            return f"{first} {last}".strip() or creator_id
        except:
            return creator_id

    def send_message(self, chat_id, text):
        """Send message to a RingCentral chat"""
        try:
            self.platform.post(f'/restapi/v1.0/glip/chats/{chat_id}/posts', {
                'text': text
            })
            print(f"📤 Sent to chat {chat_id}: '{text[:60]}{'...' if len(text) > 60 else ''}'")
            return True
        except Exception as e:
            print(f"❌ Send failed: {e}")
            return False

    def log_to_memory(self, chat_id, sender_name, message_text, response_text):
        """Log important conversations to daily memory"""
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            memory_dir = os.path.join(WORKSPACE, 'memory')
            os.makedirs(memory_dir, exist_ok=True)
            memory_file = os.path.join(memory_dir, f'{today}.md')

            timestamp = datetime.now().strftime('%H:%M')
            entry = f"\n### RingCentral ({timestamp})\n- **{sender_name}:** {message_text[:200]}\n- **Amber:** {response_text[:200]}\n"

            with open(memory_file, 'a') as f:
                f.write(entry)
        except Exception as e:
            print(f"⚠️ Memory log error: {e}")

    async def handle_new_message(self, chat_id, creator_id, text):
        """Handle a new incoming message"""
        # Skip my own messages
        if creator_id == MY_USER_ID:
            return

        # Skip empty messages
        if not text or not text.strip():
            return

        print(f"💬 [{chat_id}] New message from {creator_id}: '{text[:80]}'")

        # Get sender name
        sender_name = self.get_sender_name(creator_id)

        # Load chat history
        history = load_chat_history(chat_id)

        # Add incoming message to history
        history.append({
            'role': 'user',
            'sender_id': creator_id,
            'sender_name': sender_name,
            'text': text,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'is_me': False
        })

        # Generate AI response
        print(f"🤖 Generating response for {sender_name}...")
        response_text = generate_response(text, history, sender_name)

        if response_text:
            # Send response to RingCentral
            sent = self.send_message(chat_id, response_text)

            if sent:
                # Add my response to history
                history.append({
                    'role': 'assistant',
                    'text': response_text,
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'is_me': True
                })

                # Log to daily memory
                self.log_to_memory(chat_id, sender_name, text, response_text)

        else:
            print(f"⚠️ No response generated for: '{text[:50]}'")

        # Save updated history
        save_chat_history(chat_id, history)

    async def process_ws_message(self, raw_data):
        """Process incoming WebSocket message"""
        try:
            data = json.loads(raw_data) if isinstance(raw_data, str) else raw_data

            # Handle list format (initial connection response)
            if isinstance(data, list):
                for item in data:
                    msg_type = item.get('type', '')
                    if msg_type == 'ConnectionDetails':
                        print("✅ WebSocket connection confirmed")
                return

            # Handle notification format
            msg_type = data.get('type', '')

            if msg_type == 'ServerNotification':
                event = data.get('event', '')
                body = data.get('body', {})

                if '/restapi/v1.0/glip/posts' in event:
                    chat_id = body.get('groupId', '')
                    creator_id = body.get('creatorId', '')
                    text = body.get('text', '')

                    if chat_id and creator_id and text:
                        await self.handle_new_message(chat_id, creator_id, text)

        except Exception as e:
            print(f"❌ WebSocket message processing error: {e}")
            import traceback
            traceback.print_exc()

    async def run(self):
        """Main service loop with WebSocket connection and auto-reconnect"""
        self.running = True
        print("🚀 RingCentral Conversation Service v2 starting...")

        while self.running:
            try:
                # Authenticate
                self.authenticate()

                # Get WebSocket credentials
                ws_creds = self.get_ws_credentials()
                print(f"✅ WebSocket credentials obtained (expires in {ws_creds['expires']}s)")

                # Connect via aiohttp WebSocket
                timeout = aiohttp.ClientTimeout(total=None, connect=30)
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    headers = {
                        'Authorization': f"Bearer {ws_creds['token']}",
                        'User-Agent': 'OpenClaw-Amber/2.0'
                    }

                    async with session.ws_connect(
                        ws_creds['uri'],
                        headers=headers,
                        heartbeat=30
                    ) as ws:
                        print("🔌 WebSocket connected!")

                        # Subscribe to message events for ALL chats
                        subscription = {
                            'type': 'ClientRequest',
                            'messageId': f"sub-{int(datetime.now().timestamp())}",
                            'method': 'POST',
                            'path': '/restapi/v1.0/subscription',
                            'body': {
                                'eventFilters': ['/restapi/v1.0/glip/posts'],
                                'deliveryMode': {'transportType': 'WebSocket'}
                            }
                        }

                        await ws.send_str(json.dumps(subscription))
                        print("📋 Subscribed to ALL chat message events")
                        print("📱 RingCentral Conversation Service v2 is LIVE!")
                        print("   Listening for messages across all chats...")

                        # Reset reconnect delay on successful connection
                        self.reconnect_delay = 5

                        # Message processing loop
                        async for msg in ws:
                            if not self.running:
                                break

                            if msg.type == aiohttp.WSMsgType.TEXT:
                                await self.process_ws_message(msg.data)
                            elif msg.type == aiohttp.WSMsgType.ERROR:
                                print(f"❌ WebSocket error: {ws.exception()}")
                                break

                        print("⚠️ WebSocket connection closed")

            except asyncio.CancelledError:
                print("👋 Service cancelled")
                break
            except Exception as e:
                print(f"❌ Service error: {e}")
                import traceback
                traceback.print_exc()

            if self.running:
                print(f"🔄 Reconnecting in {self.reconnect_delay}s...")
                await asyncio.sleep(self.reconnect_delay)
                self.reconnect_delay = min(self.reconnect_delay * 2, 300)

        print("👋 RingCentral Conversation Service v2 stopped")

    def stop(self):
        self.running = False


async def main():
    # Load all credentials from env file (includes ANTHROPIC_API_KEY)
    try:
        with open(ENV_FILE, 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
    except Exception as e:
        print(f"⚠️ Error loading env file: {e}")

    if not os.environ.get('ANTHROPIC_API_KEY'):
        print("❌ No ANTHROPIC_API_KEY found. Add it to .env-ringcentral")
        sys.exit(1)

    print(f"✅ Anthropic API key loaded: {os.environ['ANTHROPIC_API_KEY'][:15]}...")

    service = RingCentralService()

    if not service.creds:
        print("❌ Could not load RingCentral credentials")
        sys.exit(1)

    # Handle shutdown signals
    def signal_handler(sig, frame):
        print("\n👋 Shutdown signal received...")
        service.stop()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        await service.run()
    except KeyboardInterrupt:
        print("\n👋 Interrupted")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Stopped")
    except Exception as e:
        print(f"❌ Failed to start: {e}")
        sys.exit(1)

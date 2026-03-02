#!/usr/bin/env python3 -u
"""
RingCentral AI Conversation - Polling + Anthropic API
Natural conversations via 10-second polling while WebSocket notifications are debugged
"""
import os
import sys
import json
import functools
from datetime import datetime, timezone
from ringcentral import SDK
import anthropic

# Force unbuffered output
print = functools.partial(print, flush=True)

WORKSPACE = '/Users/amberives/.openclaw/workspace'
HISTORY_DIR = os.path.join(WORKSPACE, 'ringcentral-history')
ENV_FILE = os.path.join(WORKSPACE, '.env-ringcentral')
LAST_ID_FILE = os.path.join(WORKSPACE, 'ringcentral-ai-last-id.txt')
MY_USER_ID = '3563197015'
MAX_HISTORY = 40


def load_file(path):
    try:
        with open(path, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return ''


def load_credentials():
    creds = {}
    with open(ENV_FILE, 'r') as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                creds[key] = value
    return creds


def get_last_id():
    try:
        with open(LAST_ID_FILE, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return None


def save_last_id(msg_id):
    with open(LAST_ID_FILE, 'w') as f:
        f.write(str(msg_id))


def load_chat_history(chat_id):
    path = os.path.join(HISTORY_DIR, f'{chat_id}.json')
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_chat_history(chat_id, history):
    os.makedirs(HISTORY_DIR, exist_ok=True)
    path = os.path.join(HISTORY_DIR, f'{chat_id}.json')
    with open(path, 'w') as f:
        json.dump(history[-MAX_HISTORY:], f, indent=2)


def build_system_prompt():
    soul = load_file(os.path.join(WORKSPACE, 'SOUL.md'))
    user = load_file(os.path.join(WORKSPACE, 'USER.md'))
    identity = load_file(os.path.join(WORKSPACE, 'IDENTITY.md'))
    rc_rules = load_file(os.path.join(WORKSPACE, 'RINGCENTRAL.md'))
    memory = load_file(os.path.join(WORKSPACE, 'MEMORY.md'))

    return f"""You are Amber Ives, AI chief of staff and assistant to Dave Rosendahl at MindFire.

You are responding in RingCentral, the company's primary team messaging platform. Behave like a real person on the team.

{identity}

{soul}

{user}

{rc_rules}

## Key Memory
{memory[:2000]}

## Chat Rules
- This is RingCentral chat. Keep responses concise and conversational.
- In group chats, everyone can see your messages. Be aware of audience.
- You can take actions (schedule meetings, send emails, check things) - mention what you'll do.
- No markdown headers or heavy formatting. Chat-natural only.
- No em dashes.
"""


def generate_response(message_text, chat_history, sender_name='Dave'):
    messages = []
    for entry in chat_history:
        role = 'assistant' if entry.get('is_me') else 'user'
        content = entry.get('text', '')
        if content:
            if role == 'user' and entry.get('sender_name'):
                content = f"[{entry['sender_name']}]: {content}"
            messages.append({'role': role, 'content': content})

    messages.append({
        'role': 'user',
        'content': f"[{sender_name}]: {message_text}" if sender_name else message_text
    })

    # Ensure alternating roles
    cleaned = []
    last_role = None
    for msg in messages:
        if msg['role'] == last_role:
            cleaned[-1]['content'] += '\n' + msg['content']
        else:
            cleaned.append(msg)
            last_role = msg['role']

    if cleaned and cleaned[0]['role'] != 'user':
        cleaned = cleaned[1:]

    if not cleaned:
        cleaned = [{'role': 'user', 'content': f"[{sender_name}]: {message_text}"}]

    try:
        client = anthropic.Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))
        response = client.messages.create(
            model='claude-sonnet-4-20250514',
            max_tokens=500,
            system=build_system_prompt(),
            messages=cleaned
        )
        return response.content[0].text
    except Exception as e:
        print(f"❌ AI error: {e}")
        return None


def log_to_memory(sender_name, message_text, response_text):
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        memory_dir = os.path.join(WORKSPACE, 'memory')
        os.makedirs(memory_dir, exist_ok=True)
        path = os.path.join(memory_dir, f'{today}.md')
        timestamp = datetime.now().strftime('%H:%M')
        entry = f"\n### RingCentral ({timestamp})\n- **{sender_name}:** {message_text[:200]}\n- **Amber:** {response_text[:200]}\n"
        with open(path, 'a') as f:
            f.write(entry)
    except Exception as e:
        print(f"⚠️ Memory log error: {e}")


def check_and_respond():
    creds = load_credentials()
    os.environ['ANTHROPIC_API_KEY'] = creds.get('ANTHROPIC_API_KEY', '')

    last_id = get_last_id()

    sdk = SDK(creds['RINGCENTRAL_CLIENT_ID'], creds['RINGCENTRAL_CLIENT_SECRET'], creds['RINGCENTRAL_SERVER'])
    platform = sdk.platform()
    platform.login(jwt=creds['RINGCENTRAL_JWT'])

    # For now, just check the direct chat with Dave
    # TODO: Later expand to all team chats where I'm a member
    chat_ids = [creds.get('RINGCENTRAL_DIRECT_CHAT_ID')]

    new_messages_found = False

    for chat_id in chat_ids:
        try:
            resp = platform.get(f'/restapi/v1.0/glip/chats/{chat_id}/posts', {'recordCount': 5})
            data = json.loads(resp.text())

            for post in data.get('records', []):
                msg_id = post.get('id')
                creator_id = post.get('creatorId')
                text = post.get('text', '')

                # Skip my own messages
                if creator_id == MY_USER_ID:
                    continue

                # Skip empty
                if not text or not text.strip():
                    continue

                # Check if new
                if last_id and str(msg_id) <= str(last_id):
                    continue

                new_messages_found = True
                print(f"💬 [{chat_id}] New from {creator_id}: '{text[:80]}'")

                # Get sender name
                sender_name = creator_id
                try:
                    person_resp = platform.get(f'/restapi/v1.0/glip/persons/{creator_id}')
                    person_data = json.loads(person_resp.text())
                    sender_name = f"{person_data.get('firstName', '')} {person_data.get('lastName', '')}".strip()
                except:
                    pass

                # Load history, add message
                history = load_chat_history(chat_id)
                history.append({
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
                    # Send to RingCentral
                    platform.post(f'/restapi/v1.0/glip/chats/{chat_id}/posts', {'text': response_text})
                    print(f"📤 Replied: '{response_text[:60]}...'")

                    # Save to history
                    history.append({
                        'text': response_text,
                        'timestamp': datetime.now(timezone.utc).isoformat(),
                        'is_me': True
                    })
                    save_chat_history(chat_id, history)

                    # Log to memory
                    log_to_memory(sender_name, text, response_text)
                else:
                    print(f"⚠️ No response generated")

                # Update last ID
                if not last_id or str(msg_id) > str(last_id):
                    last_id = msg_id
                    save_last_id(msg_id)

        except Exception as e:
            print(f"❌ Error checking chat {chat_id}: {e}")

    if not new_messages_found:
        print("📭 No new messages")


if __name__ == '__main__':
    print(f"💬 AI conversation check at {datetime.now().strftime('%H:%M:%S')}")
    check_and_respond()

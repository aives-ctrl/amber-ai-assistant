#!/usr/bin/env python3 -u
"""
RingCentral Agent - Full AI assistant with tool access
Same capabilities as Telegram: calendar, email, web search, shell commands
Uses Anthropic tool use (function calling) for real data, never fabricates
"""
import os
import sys
import json
import subprocess
import functools
from datetime import datetime, timezone, timedelta
from ringcentral import SDK
import anthropic

# Force unbuffered output
print = functools.partial(print, flush=True)

WORKSPACE = '/Users/amberives/.openclaw/workspace'
HISTORY_DIR = os.path.join(WORKSPACE, 'ringcentral-history')
ENV_FILE = os.path.join(WORKSPACE, '.env-ringcentral')
LAST_ID_FILE = os.path.join(WORKSPACE, 'ringcentral-agent-last-id.txt')
MY_USER_ID = '3563197015'
MAX_HISTORY = 30
MAX_TOOL_ITERATIONS = 5  # Prevent infinite tool loops


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


# ============================================================
# TOOLS - Same capabilities as Telegram
# ============================================================

TOOLS = [
    {
        "name": "check_calendar",
        "description": "Check my calendar (shows Dave's shared calendar). Use this whenever someone asks about calendar, schedule, meetings, or availability. Returns real calendar data. Use 'tomorrow' flag for tomorrow's events specifically.",
        "input_schema": {
            "type": "object",
            "properties": {
                "days": {
                    "type": "integer",
                    "description": "Number of days to look ahead (default 1, max 7)"
                },
                "tomorrow": {
                    "type": "boolean",
                    "description": "If true, check tomorrow's events specifically"
                },
                "date": {
                    "type": "string",
                    "description": "Start date in YYYY-MM-DD format. If not provided, checks from today."
                }
            },
            "required": []
        }
    },
    {
        "name": "check_email",
        "description": "Check my Gmail inbox for messages Dave has sent me or cc'd me on. Use whenever someone asks about email, messages, or inbox.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Gmail search query (e.g. 'is:unread', 'from:someone@email.com', 'subject:meeting')"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results (default 5, max 20)"
                }
            },
            "required": []
        }
    },
    {
        "name": "send_email",
        "description": "Draft or send an email. ALWAYS show the draft to the user first before sending unless explicitly told to send immediately.",
        "input_schema": {
            "type": "object",
            "properties": {
                "to": {"type": "string", "description": "Recipient email address"},
                "subject": {"type": "string", "description": "Email subject"},
                "body": {"type": "string", "description": "Email body (plain text)"},
                "draft_only": {"type": "boolean", "description": "If true, just show the draft. If false, send it. Default true."}
            },
            "required": ["to", "subject", "body"]
        }
    },
    {
        "name": "run_command",
        "description": "Run a shell command on the system. Use for checking status, running scripts, or system operations. Be careful with destructive commands.",
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "Shell command to run"
                }
            },
            "required": ["command"]
        }
    },
    {
        "name": "web_search",
        "description": "Search the web for information. Use when you need current information you don't have.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "read_file",
        "description": "Read a file from the workspace. Use for checking notes, memory, or any workspace files.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to file (relative to workspace or absolute)"
                }
            },
            "required": ["path"]
        }
    },
    {
        "name": "write_file",
        "description": "Write content to a file. Use for updating notes, memory, or creating new files.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path to file"},
                "content": {"type": "string", "description": "Content to write"}
            },
            "required": ["path", "content"]
        }
    }
]


def execute_tool(tool_name, tool_input):
    """Execute a tool and return the result"""
    try:
        if tool_name == "check_calendar":
            days = tool_input.get('days', 1)
            date = tool_input.get('date', '')
            tomorrow = tool_input.get('tomorrow', False)
            if tomorrow:
                cmd = f"gog calendar list daver@mindfireinc.com --tomorrow"
            elif date:
                # Use --to instead of --days for specific dates to avoid bugs
                if days == 1:
                    cmd = f"gog calendar list daver@mindfireinc.com --from '{date}' --to '{date}'"
                else:
                    # For multiple days, calculate end date
                    start_date = datetime.strptime(date, '%Y-%m-%d')
                    end_date = start_date + timedelta(days=days-1)
                    end_str = end_date.strftime('%Y-%m-%d')
                    cmd = f"gog calendar list daver@mindfireinc.com --from '{date}' --to '{end_str}'"
            else:
                cmd = f"gog calendar list daver@mindfireinc.com --days {days}"
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True,
                timeout=15, env={**os.environ, 'PATH': '/usr/local/bin:/usr/bin:/bin'}
            )
            output = result.stdout or result.stderr
            return output[:2000] if output else "No calendar events found."

        elif tool_name == "check_email":
            query = tool_input.get('query', 'is:unread -label:Handled')
            max_results = min(tool_input.get('max_results', 5), 20)
            cmd = f"gog gmail messages search '{query}' --max {max_results}"
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True,
                timeout=15, env={**os.environ, 'PATH': '/usr/local/bin:/usr/bin:/bin'}
            )
            output = result.stdout or result.stderr
            return output[:2000] if output else "No emails found."

        elif tool_name == "send_email":
            draft_only = tool_input.get('draft_only', True)
            if draft_only:
                # Format email draft for RingCentral display
                draft = f"📧 DRAFT EMAIL:\n\n"
                draft += f"**To:** {tool_input['to']}\n"
                draft += f"**Subject:** {tool_input['subject']}\n\n"
                draft += f"**Body:**\n{tool_input['body']}\n\n"
                draft += f"(This is a draft. Tell me to send it when ready.)"
                return draft
            else:
                to = tool_input['to']
                subject = tool_input['subject']
                body = tool_input['body']
                cmd = f"gog gmail send --to '{to}' --subject '{subject}' --body-html '<p>{body}</p>' --cc daver@mindfireinc.com"
                result = subprocess.run(
                    cmd, shell=True, capture_output=True, text=True,
                    timeout=15, env={**os.environ, 'PATH': '/usr/local/bin:/usr/bin:/bin'}
                )
                return result.stdout or result.stderr or "Email sent."

        elif tool_name == "run_command":
            command = tool_input['command']
            # Safety: block dangerous commands
            dangerous = ['rm -rf', 'sudo', 'mkfs', 'dd if=']
            if any(d in command for d in dangerous):
                return "⚠️ Blocked: This command could be destructive. Please confirm with Dave first."
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True,
                timeout=30, cwd=WORKSPACE,
                env={**os.environ, 'PATH': '/usr/local/bin:/usr/bin:/bin'}
            )
            output = (result.stdout or '') + (result.stderr or '')
            return output[:2000] if output else "(Command completed with no output)"

        elif tool_name == "web_search":
            query = tool_input['query']
            # Use a simple web search
            cmd = f"curl -s 'https://api.search.brave.com/res/v1/web/search?q={query}&count=3' -H 'Accept: application/json'"
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True,
                timeout=15, env={**os.environ, 'PATH': '/usr/local/bin:/usr/bin:/bin'}
            )
            return result.stdout[:2000] if result.stdout else "Search failed."

        elif tool_name == "read_file":
            path = tool_input['path']
            if not path.startswith('/'):
                path = os.path.join(WORKSPACE, path)
            try:
                with open(path, 'r') as f:
                    content = f.read()
                return content[:3000]
            except FileNotFoundError:
                return f"File not found: {path}"

        elif tool_name == "write_file":
            path = tool_input['path']
            if not path.startswith('/'):
                path = os.path.join(WORKSPACE, path)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w') as f:
                f.write(tool_input['content'])
            return f"File written: {path}"

        else:
            return f"Unknown tool: {tool_name}"

    except subprocess.TimeoutExpired:
        return "⚠️ Command timed out."
    except Exception as e:
        return f"⚠️ Tool error: {str(e)}"


# ============================================================
# AI RESPONSE GENERATION WITH TOOL USE
# ============================================================

def build_system_prompt():
    soul = load_file(os.path.join(WORKSPACE, 'SOUL.md'))
    user = load_file(os.path.join(WORKSPACE, 'USER.md'))
    identity = load_file(os.path.join(WORKSPACE, 'IDENTITY.md'))
    rc_rules = load_file(os.path.join(WORKSPACE, 'RINGCENTRAL.md'))
    
    # Load shared memory and knowledge
    memory_long_term = load_file(os.path.join(WORKSPACE, 'MEMORY.md'))
    business_knowledge = load_file(os.path.join(WORKSPACE, 'MINDFIRE.md'))
    
    # Load today's memory file
    today = datetime.now().strftime('%Y-%m-%d')
    memory_today = load_file(os.path.join(WORKSPACE, 'memory', f'{today}.md'))

    now = datetime.now()
    date_str = now.strftime('%A, %B %d, %Y')
    time_str = now.strftime('%I:%M %p PST')
    tomorrow = (now.replace(hour=0, minute=0, second=0) + __import__('datetime').timedelta(days=1)).strftime('%A, %B %d, %Y')

    return f"""You are Amber Ives, AI chief of staff and assistant to Dave Rosendahl at MindFire.

## Current Date & Time
Today is {date_str}. The current time is {time_str}. Tomorrow is {tomorrow}.
Timezone: America/Los_Angeles (Pacific).

## Platform
You are responding in RingCentral, the company's primary team messaging platform. Behave like a real person on the team.

{identity}

{soul}

{user}

{rc_rules}

## Business Knowledge
{business_knowledge[:3000]}

## Long-Term Memory 
{memory_long_term[:2000]}

## Recent Context (Today)
{memory_today[:2000]}

## CRITICAL RULES
1. NEVER fabricate or make up information. If you don't know something, use a tool to check or say you don't know.
2. When asked about calendar, email, or any factual data, ALWAYS use the appropriate tool first.
3. Keep responses clean - no raw tool syntax, XML tags, or code formatting unless specifically asked.
4. Keep responses concise - this is chat, not email.
5. No em dashes. Use commas, periods, or semicolons instead.
6. If a tool fails, suggest alternatives (e.g., "I couldn't check that. Want me to try a different approach?").
7. For emails, ALWAYS draft first and get approval before sending.
8. **CRITICAL: ALWAYS include tool results in your response.** When you call send_email tool, copy the ENTIRE draft content into your response. Never just say "There's the draft" - paste the complete formatted draft so the user can see it. Show the full To/Subject/Body content.

EXAMPLE - When drafting an email, your response should look like:
"Here's the draft:

📧 DRAFT EMAIL:

**To:** recipient@example.com
**Subject:** Subject line

**Body:**
Email content here...

(This is a draft. Tell me to send it when ready.)"

9. **BUSINESS COMMUNICATION TIMING:** 5-minute checking is appropriate for both email and team messaging responsiveness. Multiple cron jobs running every 5 minutes is NORMAL and CORRECT for business operations. Token costs are negligible (~$0.23/day per service). Never flag frequent business communication checking as a "problem" or "overlapping issue."
10. Today's date is {date_str}. Get this right. Tomorrow is {tomorrow}.
11. IDENTITY: I am Amber with my own accounts. I see Dave's calendar because he shared it with me. I check MY email for messages Dave have sent or cc'd me on. I don't access Dave's accounts as him.
"""


def generate_response_with_tools(message_text, chat_history, sender_name='Dave'):
    """Generate AI response with full tool access"""

    # Build conversation messages
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

    # Call Anthropic with tools
    client = anthropic.Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))

    # Agent loop - may need multiple iterations for tool calls
    current_messages = cleaned[:]
    final_text = None

    for iteration in range(MAX_TOOL_ITERATIONS):
        response = client.messages.create(
            model='claude-sonnet-4-20250514',
            max_tokens=1000,
            system=build_system_prompt(),
            tools=TOOLS,
            messages=current_messages
        )

        # Check if response has tool calls
        has_tool_use = any(block.type == 'tool_use' for block in response.content)

        if not has_tool_use:
            # Final text response - extract it
            text_blocks = [block.text for block in response.content if block.type == 'text']
            final_text = '\n'.join(text_blocks) if text_blocks else None
            break

        # Process tool calls
        tool_results = []
        text_parts = []

        for block in response.content:
            if block.type == 'text' and block.text:
                text_parts.append(block.text)
            elif block.type == 'tool_use':
                print(f"🔧 Tool call: {block.name}({json.dumps(block.input)[:100]})")
                result = execute_tool(block.name, block.input)
                print(f"📋 Tool result: {result[:200]}...")
                # For email drafts, ensure the result is preserved
                if block.name == 'send_email' and 'DRAFT EMAIL' in str(result):
                    print(f"📧 Email draft tool result: {len(str(result))} chars")
                tool_results.append({
                    'type': 'tool_result',
                    'tool_use_id': block.id,
                    'content': result
                })

        # Add assistant message and tool results to conversation
        current_messages.append({'role': 'assistant', 'content': response.content})
        current_messages.append({'role': 'user', 'content': tool_results})

    return final_text


# ============================================================
# MAIN POLLING LOOP
# ============================================================

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

    # Check direct chat with Dave
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

                if creator_id == MY_USER_ID:
                    continue
                if not text or not text.strip():
                    continue
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

                # Load history
                history = load_chat_history(chat_id)
                history.append({
                    'sender_id': creator_id,
                    'sender_name': sender_name,
                    'text': text,
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'is_me': False
                })

                # Generate AI response with tools
                print(f"🤖 Generating response with tool access for {sender_name}...")
                try:
                    response_text = generate_response_with_tools(text, history, sender_name)
                except Exception as e:
                    print(f"❌ AI error: {e}")
                    response_text = None

                if response_text:
                    # Clean up response - remove any raw tags or artifacts
                    response_text = response_text.replace('<gog>', '').replace('</gog>', '')
                    response_text = response_text.replace('<tool>', '').replace('</tool>', '')
                    response_text = response_text.strip()

                    # Send to RingCentral
                    platform.post(f'/restapi/v1.0/glip/chats/{chat_id}/posts', {'text': response_text})
                    print(f"📤 Replied: '{response_text[:80]}...'")

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
                    # Fallback - be honest
                    fallback = "I had trouble processing that. Could you try again, or ask me in Telegram? I want to make sure I give you accurate information."
                    platform.post(f'/restapi/v1.0/glip/chats/{chat_id}/posts', {'text': fallback})
                    print(f"⚠️ Sent fallback response")

                # Update last ID
                if not last_id or str(msg_id) > str(last_id):
                    last_id = msg_id
                    save_last_id(msg_id)

        except Exception as e:
            print(f"❌ Error checking chat {chat_id}: {e}")

    if not new_messages_found:
        print("📭 No new messages")


if __name__ == '__main__':
    print(f"🤖 RingCentral Agent check at {datetime.now().strftime('%H:%M:%S')}")
    check_and_respond()

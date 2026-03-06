#!/bin/bash

# mcp-write.sh -- Wrapper for WRITE MCP operations (requires Dave's exec-approval)
# This script is NOT on the exec allowlist — every call triggers approval via Telegram.
# Read operations should use mcp-read.sh instead (auto-approved).
#
# Uses `uvx workspace-mcp --cli --args` for direct tool invocation (no JSON-RPC handshake).
#
# Usage: mcp-write.sh <tool_name> [--param value ...] [--body-file <path>] [--json-body <raw_json>]
#
# Examples:
#   # Send a new email (inline body — use single quotes in HTML attributes!)
#   mcp-write.sh send_gmail_message \
#     --to "recipient@example.com" \
#     --cc "daver@mindfireinc.com" \
#     --subject "Subject here" \
#     --body "<div style='font-size:18px'><p>Body here.</p></div>" \
#     --body_format "html"
#
#   # Send with body from file (PREFERRED — avoids $dollar sign and quote escaping issues)
#   mcp-write.sh send_gmail_message \
#     --to "recipient@example.com" \
#     --subject "Subject here" \
#     --body-file /tmp/email-body.html \
#     --body_format "html"
#
#   # Send a reply (with threading)
#   mcp-write.sh send_gmail_message \
#     --to "original-sender@example.com" \
#     --cc "daver@mindfireinc.com,other@example.com" \
#     --subject "RE: Original Subject" \
#     --body "<div style='font-size:18px'><p>Reply body.</p></div>" \
#     --body_format "html" \
#     --thread_id "18abc123def" \
#     --in_reply_to "18abc123def" \
#     --references "<message-id-header>"
#
#   # Create a calendar event (uses manage_event with action=create)
#   mcp-write.sh manage_event \
#     --action "create" \
#     --calendar_id "daver@mindfireinc.com" \
#     --summary "Meeting Name" \
#     --start_time "2026-03-07T10:00:00" \
#     --end_time "2026-03-07T11:00:00" \
#     --description "Meeting description"
#
#   # For complex arguments (attendees arrays, etc.), use --json-body:
#   mcp-write.sh manage_event --json-body '{"action":"create","calendar_id":"daver@mindfireinc.com","summary":"Team Meeting","start_time":"2026-03-07T10:00:00","end_time":"2026-03-07T11:00:00","attendees":["a@example.com","b@example.com"]}'

# --- Configuration ---
USER_EMAIL="aives@mindfiremail.info"

# --- Load OAuth credentials ---
# Non-interactive shells (like OpenClaw agents) don't source .zshrc.
# Source from ~/.mcp-env if env vars aren't already set.
if [ -z "${GOOGLE_OAUTH_CLIENT_ID:-}" ] || [ -z "${GOOGLE_OAUTH_CLIENT_SECRET:-}" ]; then
    if [ -f "$HOME/.mcp-env" ]; then
        source "$HOME/.mcp-env"
    elif [ -f "/Users/amberives/.mcp-env" ]; then
        source "/Users/amberives/.mcp-env"
    fi
fi

if [ -z "${GOOGLE_OAUTH_CLIENT_ID:-}" ] || [ -z "${GOOGLE_OAUTH_CLIENT_SECRET:-}" ]; then
    echo "ERROR: OAuth credentials not found."
    echo "Create ~/.mcp-env with:"
    echo '  export GOOGLE_OAUTH_CLIENT_ID="your-client-id"'
    echo '  export GOOGLE_OAUTH_CLIENT_SECRET="your-client-secret"'
    exit 1
fi

# --- Allowed write tools (anything not here is blocked) ---
ALLOWED_TOOLS=(
    "send_gmail_message"
    "manage_event"
    "manage_gmail_label"
    "batch_modify_gmail_message_labels"
)

# --- Parse arguments ---
TOOL_NAME="$1"
shift

if [ -z "$TOOL_NAME" ]; then
    echo "ERROR: No tool name provided."
    echo "Usage: mcp-write.sh <tool_name> [--param value ...]"
    echo "Allowed tools: ${ALLOWED_TOOLS[*]}"
    exit 1
fi

# --- Check allowlist ---
ALLOWED=false
for tool in "${ALLOWED_TOOLS[@]}"; do
    if [ "$TOOL_NAME" = "$tool" ]; then
        ALLOWED=true
        break
    fi
done

if [ "$ALLOWED" != "true" ]; then
    echo "ERROR: Tool '$TOOL_NAME' is not a recognized write operation."
    echo "Allowed: ${ALLOWED_TOOLS[*]}"
    echo "For read operations, use mcp-read.sh instead."
    exit 1
fi

# --- Check for --json-body and --body-file modes ---
JSON_BODY=""
BODY_FILE=""
REMAINING_ARGS=()

while [ $# -gt 0 ]; do
    if [ "$1" = "--json-body" ]; then
        JSON_BODY="$2"
        shift 2
    elif [ "$1" = "--body-file" ]; then
        BODY_FILE="$2"
        shift 2
    else
        REMAINING_ARGS+=("$1")
        shift
    fi
done

# Restore remaining args for --param value parsing
set -- "${REMAINING_ARGS[@]}"

# --- Handle --body-file: read file content and inject as --body parameter ---
# This avoids ALL shell escaping issues (dollar signs, backticks, quotes, etc.)
# because the file content is read by the script, not parsed by bash.
if [ -n "$BODY_FILE" ]; then
    if [ ! -f "$BODY_FILE" ]; then
        echo "ERROR: Body file not found: $BODY_FILE"
        exit 1
    fi
    # Read file content — will be added to PARAMS after the loop below
    BODY_FROM_FILE=$(cat "$BODY_FILE")
fi

if [ -n "$JSON_BODY" ]; then
    # Inject user_google_email if not already present
    ARGS_JSON=$(python3 -c "
import json, sys
d = json.loads(sys.argv[1])
if 'user_google_email' not in d:
    d['user_google_email'] = sys.argv[2]
print(json.dumps(d))
" "$JSON_BODY" "$USER_EMAIL")
else
    # --- Build JSON arguments from --param value pairs ---
    # Use python3 for reliable JSON construction (no shell escaping bugs)
    PARAMS=()

    # Add user_google_email automatically for ALL tools
    PARAMS+=("user_google_email" "$USER_EMAIL")

    while [ $# -gt 0 ]; do
        case "$1" in
            --*)
                PARAM_NAME="${1#--}"
                PARAM_VALUE="$2"
                if [ -z "$PARAM_VALUE" ]; then
                    echo "ERROR: Missing value for parameter $1"
                    exit 1
                fi
                PARAMS+=("$PARAM_NAME" "$PARAM_VALUE")
                shift 2
                ;;
            *)
                echo "ERROR: Unexpected argument: $1 (use --param value format)"
                exit 1
                ;;
        esac
    done

    # Inject body from file if --body-file was used
    if [ -n "$BODY_FILE" ]; then
        PARAMS+=("body" "$BODY_FROM_FILE")
    fi

    # Build JSON safely using python3
    # Handles: strings, ints, JSON arrays (values starting with [), JSON objects (values starting with {)
    ARGS_JSON=$(python3 -c "
import json, sys
params = sys.argv[1:]
d = {}
for i in range(0, len(params), 2):
    key = params[i]
    val = params[i+1]
    # Try to parse as JSON (handles arrays like '[\"Handled\"]' and objects)
    if val.startswith('[') or val.startswith('{'):
        try:
            val = json.loads(val)
        except json.JSONDecodeError:
            pass  # Keep as string if not valid JSON
    else:
        # Try to parse as int
        try:
            val = int(val)
        except ValueError:
            pass
    d[key] = val

# --- AUTO-DETECT HTML: if body looks like HTML but body_format is missing, add it ---
# This catches quoting errors where --body_format 'html' gets swallowed by shell parsing.
# Same philosophy: make the wrong thing impossible.
if 'body' in d and isinstance(d['body'], str) and d['body'].strip().startswith('<') and 'body_format' not in d:
    d['body_format'] = 'html'
    print('WARNING: body looks like HTML but body_format was missing. Auto-added body_format=html.', file=sys.stderr)

print(json.dumps(d))
" "${PARAMS[@]}")

    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to build JSON arguments"
        exit 1
    fi
fi

# --- SAFETY: Block delete actions on manage_event ---
if [ "$TOOL_NAME" = "manage_event" ]; then
    if echo "$ARGS_JSON" | python3 -c "
import json, sys
d = json.load(sys.stdin)
if d.get('action', '').lower() == 'delete':
    print('BLOCKED')
    sys.exit(1)
" 2>/dev/null; then
        : # not blocked, continue
    else
        echo "ERROR: manage_event with action='delete' is BLOCKED. Dave must delete events manually."
        exit 1
    fi
fi

# --- Determine which MCP tools to load ---
if [[ "$TOOL_NAME" == *"gmail"* ]] || [[ "$TOOL_NAME" == *"label"* ]]; then
    MCP_TOOLS="gmail"
elif [[ "$TOOL_NAME" == *"event"* ]] || [[ "$TOOL_NAME" == *"calendar"* ]]; then
    MCP_TOOLS="calendar"
else
    MCP_TOOLS="gmail calendar"
fi

# --- Show what we're about to do (for approval visibility) ---
echo "MCP WRITE: $TOOL_NAME"
echo "Args: $ARGS_JSON"
echo "---"

# --- Execute via CLI mode ---
# --cli mode does direct tool invocation (no MCP protocol handshake needed)
# --args passes the JSON arguments to the tool
uvx workspace-mcp --tools $MCP_TOOLS --cli "$TOOL_NAME" --args "$ARGS_JSON" 2>/dev/null

EXIT_CODE=$?
if [ $EXIT_CODE -ne 0 ]; then
    echo "ERROR: MCP call failed with exit code $EXIT_CODE"
    echo "Tool: $TOOL_NAME"
    echo "Args: $ARGS_JSON"

    # SAFETY: Do NOT auto-retry send operations — the first attempt may have sent.
    # Retrying causes duplicate emails (#20). Report the error and let the user decide.
    if [ "$TOOL_NAME" = "send_gmail_message" ]; then
        echo "---"
        echo "⚠️  This was a SEND operation. The email MAY have been sent despite the error."
        echo "CHECK SENT MAIL before retrying to avoid sending duplicates."
        echo "Run: mcp-read.sh search_gmail_messages --query \"in:sent newer_than:1h\" --page_size 3"
        exit $EXIT_CODE
    fi

    # For non-send operations, retry with stderr visible for debugging
    echo "--- Retrying with debug output ---"
    uvx workspace-mcp --tools $MCP_TOOLS --cli "$TOOL_NAME" --args "$ARGS_JSON"
    exit $EXIT_CODE
fi

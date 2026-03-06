#!/bin/bash

# mcp-write.sh -- Wrapper for WRITE MCP operations (requires Dave's exec-approval)
# This script is NOT on the exec allowlist — every call triggers approval via Telegram.
# Read operations should use mcp-read.sh instead (auto-approved).
#
# Uses `uvx workspace-mcp --cli --args` for direct tool invocation (no JSON-RPC handshake).
#
# Usage: mcp-write.sh <tool_name> [--param value ...] [--json-body <raw_json>]
#
# Examples:
#   # Send a new email
#   mcp-write.sh send_gmail_message \
#     --to "recipient@example.com" \
#     --cc "daver@mindfireinc.com" \
#     --subject "Subject here" \
#     --body "<div style='font-size:18px'><p>Body here.</p></div>" \
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
#   # Create a calendar event
#   mcp-write.sh create_event \
#     --calendar_id "daver@mindfireinc.com" \
#     --summary "Meeting Name" \
#     --start "2026-03-07T10:00:00" \
#     --end "2026-03-07T11:00:00" \
#     --description "Meeting description"
#
#   # For complex arguments (attendees arrays, etc.), use --json-body:
#   mcp-write.sh create_event --json-body '{"calendar_id":"daver@mindfireinc.com","summary":"Team Meeting","start":"2026-03-07T10:00:00","end":"2026-03-07T11:00:00","attendees":["a@example.com","b@example.com"]}'

# --- Configuration ---
USER_EMAIL="aives@mindfiremail.info"

# --- Allowed write tools (anything not here is blocked) ---
ALLOWED_TOOLS=(
    "send_gmail_message"
    "create_event"
    "modify_event"
    "manage_gmail_label"
    "batch_modify_gmail_message_labels"
)

# --- Explicitly blocked tools (never allow, even if added to ALLOWED_TOOLS by mistake) ---
BLOCKED_TOOLS=(
    "delete_event"
    "delete_gmail_message"
    "trash_gmail_message"
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

# --- Check blocklist first (safety) ---
for tool in "${BLOCKED_TOOLS[@]}"; do
    if [ "$TOOL_NAME" = "$tool" ]; then
        echo "ERROR: Tool '$TOOL_NAME' is BLOCKED. Dave must do this manually."
        exit 1
    fi
done

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

# --- Check for --json-body mode ---
JSON_BODY=""
REMAINING_ARGS=()

while [ $# -gt 0 ]; do
    if [ "$1" = "--json-body" ]; then
        JSON_BODY="$2"
        shift 2
    else
        REMAINING_ARGS+=("$1")
        shift
    fi
done

# Restore remaining args for --param value parsing
set -- "${REMAINING_ARGS[@]}"

if [ -n "$JSON_BODY" ]; then
    # For --json-body mode, inject user_google_email if needed and not already present
    if [[ "$TOOL_NAME" == *"gmail"* ]] || [[ "$TOOL_NAME" == *"label"* ]]; then
        ARGS_JSON=$(python3 -c "
import json, sys
d = json.loads(sys.argv[1])
if 'user_google_email' not in d:
    d['user_google_email'] = sys.argv[2]
print(json.dumps(d))
" "$JSON_BODY" "$USER_EMAIL")
    else
        ARGS_JSON="$JSON_BODY"
    fi
else
    # --- Build JSON arguments from --param value pairs ---
    # Use python3 for reliable JSON construction (no shell escaping bugs)
    PARAMS=()

    # Add user_google_email automatically for gmail/label tools
    if [[ "$TOOL_NAME" == *"gmail"* ]] || [[ "$TOOL_NAME" == *"label"* ]]; then
        PARAMS+=("user_google_email" "$USER_EMAIL")
    fi

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

    # Build JSON safely using python3
    ARGS_JSON=$(python3 -c "
import json, sys
params = sys.argv[1:]
d = {}
for i in range(0, len(params), 2):
    key = params[i]
    val = params[i+1]
    # Try to parse as int
    try:
        val = int(val)
    except ValueError:
        pass
    d[key] = val
print(json.dumps(d))
" "${PARAMS[@]}")

    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to build JSON arguments"
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
    # Retry with stderr visible for debugging
    echo "--- Debug output ---"
    uvx workspace-mcp --tools $MCP_TOOLS --cli "$TOOL_NAME" --args "$ARGS_JSON"
    exit $EXIT_CODE
fi

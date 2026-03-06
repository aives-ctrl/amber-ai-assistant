#!/bin/bash

# mcp-read.sh -- Allowlisted wrapper for READ-ONLY MCP operations
# This script is on the exec allowlist. It ONLY runs safe, read-only MCP tool calls.
# Send/create operations MUST go through mcp-write.sh (requires Dave's approval).
#
# Uses `uvx workspace-mcp --cli --args` for direct tool invocation (no JSON-RPC handshake).
#
# Usage: mcp-read.sh <tool_name> [--param value ...]
#
# Examples:
#   mcp-read.sh search_gmail_messages --query "is:unread -label:Handled" --page_size 10
#   mcp-read.sh get_gmail_message_content --message_id "abc123"
#   mcp-read.sh get_gmail_thread_content --thread_id "abc123"
#   mcp-read.sh list_gmail_labels
#   mcp-read.sh get_events --calendar_id "daver@mindfireinc.com" --time_min "2026-03-06T00:00:00" --time_max "2026-03-06T23:59:59"
#   mcp-read.sh list_calendars
#   # For array params (label IDs), pass JSON arrays as values:
#   mcp-read.sh modify_gmail_message_labels --message_id "abc123" --add_label_ids '["Handled"]' --remove_label_ids '["UNREAD"]'

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

# --- Allowlist: read-only MCP tools ---
ALLOWED_TOOLS=(
    "search_gmail_messages"
    "get_gmail_message_content"
    "get_gmail_messages_content_batch"
    "get_gmail_thread_content"
    "get_gmail_threads_content_batch"
    "list_gmail_labels"
    "modify_gmail_message_labels"
    "draft_gmail_message"
    "get_events"
    "list_calendars"
)

# --- Parse arguments ---
TOOL_NAME="$1"
shift

if [ -z "$TOOL_NAME" ]; then
    echo "ERROR: No tool name provided."
    echo "Usage: mcp-read.sh <tool_name> [--param value ...]"
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
    echo "ERROR: Tool '$TOOL_NAME' is not allowed in read-only mode."
    echo "Allowed tools: ${ALLOWED_TOOLS[*]}"
    echo "For send/create operations, use mcp-write.sh (requires Dave's approval)."
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

set -- "${REMAINING_ARGS[@]}"

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

    # Add user_google_email automatically for ALL tools (every MCP tool needs it)
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

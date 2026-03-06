#!/bin/bash

# mcp-read.sh -- Allowlisted wrapper for READ-ONLY MCP operations
# This script is on the exec allowlist. It ONLY runs safe, read-only MCP tool calls.
# Send/create operations MUST go through mcp-write.sh (requires Dave's approval).
#
# Usage: mcp-read.sh <tool_name> [--param value ...]
#
# Examples:
#   mcp-read.sh search_gmail_messages --query "is:unread -label:Handled" --max_results 10
#   mcp-read.sh get_gmail_message_content --message_id "abc123"
#   mcp-read.sh get_gmail_thread_content --thread_id "abc123"
#   mcp-read.sh list_gmail_labels
#   mcp-read.sh get_events --calendar_id "daver@mindfireinc.com" --time_min "2026-03-06T00:00:00" --time_max "2026-03-06T23:59:59"
#   mcp-read.sh list_calendars

# --- Configuration ---
USER_EMAIL="aives@mindfiremail.info"

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

# --- Build JSON arguments from --param value pairs ---
# Always include user_google_email for Gmail tools
ARGS_JSON="{"
FIRST=true

# Add user_google_email automatically for gmail tools
if [[ "$TOOL_NAME" == *"gmail"* ]] || [[ "$TOOL_NAME" == *"label"* ]]; then
    ARGS_JSON="{\"user_google_email\": \"${USER_EMAIL}\""
    FIRST=false
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

            if [ "$FIRST" = true ]; then
                FIRST=false
            else
                ARGS_JSON="${ARGS_JSON}, "
            fi

            # Handle numeric values
            if [[ "$PARAM_VALUE" =~ ^[0-9]+$ ]]; then
                ARGS_JSON="${ARGS_JSON}\"${PARAM_NAME}\": ${PARAM_VALUE}"
            else
                ARGS_JSON="${ARGS_JSON}\"${PARAM_NAME}\": \"${PARAM_VALUE}\""
            fi
            shift 2
            ;;
        *)
            echo "ERROR: Unexpected argument: $1 (use --param value format)"
            exit 1
            ;;
    esac
done

ARGS_JSON="${ARGS_JSON}}"

# --- Determine which MCP tools to load ---
if [[ "$TOOL_NAME" == *"gmail"* ]] || [[ "$TOOL_NAME" == *"label"* ]]; then
    MCP_TOOLS="gmail"
elif [[ "$TOOL_NAME" == *"event"* ]] || [[ "$TOOL_NAME" == *"calendar"* ]]; then
    MCP_TOOLS="calendar"
else
    MCP_TOOLS="gmail calendar"
fi

# --- Build and execute MCP call ---
MCP_REQUEST="{\"method\": \"tools/call\", \"params\": {\"name\": \"${TOOL_NAME}\", \"arguments\": ${ARGS_JSON}}}"

# Execute
echo "$MCP_REQUEST" | uvx workspace-mcp --tools $MCP_TOOLS 2>/dev/null

EXIT_CODE=$?
if [ $EXIT_CODE -ne 0 ]; then
    echo "ERROR: MCP call failed with exit code $EXIT_CODE"
    echo "Tool: $TOOL_NAME"
    echo "Request: $MCP_REQUEST"
    exit $EXIT_CODE
fi

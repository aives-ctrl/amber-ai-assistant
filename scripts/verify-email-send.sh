#!/bin/bash

# verify-email-send.sh — Opus 4.6 pre-flight check for email sends
#
# Called from the email-send lobster workflow. Uses openclaw.invoke to
# call llm-task with Opus, which validates the email send parameters
# against known error patterns.
#
# REQUIRES: OPENCLAW_URL and OPENCLAW_TOKEN env vars (set by workflow)
#
# USAGE:
#   verify-email-send.sh  (reads from LOBSTER_ARG_* env vars)
#
# RETURNS: JSON on stdout with {approved, errors, warnings, summary}
#          Exit code 0 on success (even if not approved), non-zero on tool failure.

# Ensure /usr/local/bin is in PATH — lobster runs steps via /bin/sh which
# has a minimal PATH that doesn't include npm globals (openclaw.invoke) or
# homebrew binaries (jq). Without this, the script fails silently.
export PATH="/usr/local/bin:/opt/homebrew/bin:$PATH"

set -euo pipefail

# Read args from lobster env vars (safe — no shell injection)
FROM="${LOBSTER_ARG_ORIGINAL_FROM:-}"
TO="${LOBSTER_ARG_ORIGINAL_TO:-}"
CC="${LOBSTER_ARG_ORIGINAL_CC:-}"
MSG_ID="${LOBSTER_ARG_MESSAGE_ID:-}"
SUBJECT="${LOBSTER_ARG_SUBJECT:-}"
BODY_HTML="${LOBSTER_ARG_BODY_HTML:-}"
IS_REPLY="${LOBSTER_ARG_IS_REPLY:-true}"

# Build the prompt
PROMPT="You are an email send validator. Check this outgoing email for errors.

ORIGINAL EMAIL HEADERS:
- From: ${FROM}
- To: ${TO}
- CC: ${CC}

OUTGOING PARAMETERS:
- is_reply: ${IS_REPLY}
- message_id: ${MSG_ID}
- subject: ${SUBJECT}
- body_html_prefix: $(echo "$BODY_HTML" | head -c 200)

CHECK THESE RULES:
1. If is_reply=true, message_id MUST be provided (not empty). Missing message_id means a --to send was used instead of --reply-to-message-id, which breaks threading.
2. If is_reply=true, reply-all behavior is required. CC recipients must not be dropped.
3. body_html MUST start with a div that includes font-size styling (e.g., font-size:18px). Without this, Gmail renders in tiny default font.
4. Signature MUST end with exactly: Amber Ives<br>MindFire, Inc. (no title, no email address, no phone).
5. Subject for replies MUST start with RE: and match the original thread subject.
6. daver@mindfireinc.com should be CC-ed (unless Dave is already on To or CC in the original headers).
7. Body should not be empty or just a signature.

Return your verdict as JSON with: approved (bool), errors (array of strings), warnings (array of strings), summary (one-line string)."

# Use jq to safely build JSON args (handles all quoting/escaping)
ARGS_JSON=$(jq -n \
  --arg prompt "$PROMPT" \
  --arg input "$BODY_HTML" \
  '{
    "prompt": $prompt,
    "input": $input,
    "provider": "anthropic",
    "model": "claude-opus-4-6",
    "temperature": 0,
    "maxTokens": 500,
    "schema": {
      "type": "object",
      "properties": {
        "approved": {"type": "boolean", "description": "true if all checks pass"},
        "errors": {"type": "array", "items": {"type": "string"}, "description": "List of specific errors found. Empty if approved."},
        "warnings": {"type": "array", "items": {"type": "string"}, "description": "Non-blocking concerns."},
        "summary": {"type": "string", "description": "One-line verdict"}
      },
      "required": ["approved", "errors", "summary"]
    }
  }')

# Call Opus via the Gateway
openclaw.invoke --tool llm-task --action json --args-json "$ARGS_JSON"

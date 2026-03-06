#!/bin/bash

# verify-with-opus.sh — General-purpose Opus 4.6 pre-flight verification
#
# Calls Opus via openclaw.invoke (llm-task plugin) to validate parameters
# before an irreversible action. Uses a domain-specific prompt template
# with variable substitution.
#
# DESIGN: One verification mechanism, many domains. The PROMPT TEMPLATE
# makes it domain-specific, not the script. Add new templates to
# config/verify-prompts/ for new action types.
#
# REQUIRES:
#   - OpenClaw gateway running (port 18789)
#   - llm-task plugin enabled with claude-opus-4-6 in allowedModels
#   - jq installed
#   - openclaw.invoke in PATH
#
# USAGE:
#   verify-with-opus.sh <prompt-template> [--var key=value ...]
#
# EXAMPLES:
#   # Email send verification
#   verify-with-opus.sh email-send \
#     --var original_from="Alex <alex@example.com>" \
#     --var original_to="Dave <daver@mindfireinc.com>" \
#     --var original_cc="Bryan <bryan@example.com>" \
#     --var is_reply="true" \
#     --var message_id="19cbff105304bf97" \
#     --var subject="RE: Friday recap" \
#     --var has_reply_all="true" \
#     --var cc_line="daver@mindfireinc.com" \
#     --var body_html_preview="<div style=\"font-size:18px\"><p>Thanks Alex..."
#
#   # Future: calendar verification
#   verify-with-opus.sh calendar-create \
#     --var summary="Team meeting" \
#     --var attendees="alice@co.com, bob@co.com" \
#     --var start_time="2026-03-10T14:00:00Z"
#
# RETURNS:
#   stdout: JSON {approved, errors, warnings, summary}
#   exit 0: verification ran (check approved field for pass/fail)
#   exit 1: script/tool failure (couldn't run verification at all)
#
# FALLBACK: If this script fails (gateway down, openclaw.invoke missing),
# use verify-email-params.sh (bash regex checks) as a backup.

export PATH="/usr/local/bin:/opt/homebrew/bin:$PATH"
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WORKSPACE_DIR="$(dirname "$SCRIPT_DIR")"

# ── Parse arguments ──
if [[ $# -lt 1 ]]; then
  echo "Usage: verify-with-opus.sh <prompt-template> [--var key=value ...]" >&2
  echo "Templates: ls $WORKSPACE_DIR/config/verify-prompts/" >&2
  exit 1
fi

TEMPLATE_NAME="$1"
shift

TEMPLATE_FILE="$WORKSPACE_DIR/config/verify-prompts/${TEMPLATE_NAME}.md"
if [[ ! -f "$TEMPLATE_FILE" ]]; then
  echo "Error: Template not found: $TEMPLATE_FILE" >&2
  echo "Available templates:" >&2
  ls "$WORKSPACE_DIR/config/verify-prompts/" 2>/dev/null || echo "  (none)" >&2
  exit 1
fi

# Read template
PROMPT=$(cat "$TEMPLATE_FILE")

# Substitute variables: --var key=value replaces {{key}} in the template
while [[ $# -gt 0 ]]; do
  case $1 in
    --var)
      if [[ $# -lt 2 ]]; then
        echo "Error: --var requires key=value argument" >&2
        exit 1
      fi
      KEY="${2%%=*}"
      VALUE="${2#*=}"
      PROMPT="${PROMPT//\{\{$KEY\}\}/$VALUE}"
      shift 2
      ;;
    *)
      echo "Unknown arg: $1" >&2
      exit 1
      ;;
  esac
done

# Replace any remaining {{...}} with "(not provided)"
PROMPT=$(echo "$PROMPT" | sed 's/{{[^}]*}}/(not provided)/g')

# ── Call Opus via Gateway ──
ARGS_JSON=$(jq -n \
  --arg prompt "$PROMPT" \
  '{
    "prompt": $prompt,
    "input": "Verify the parameters above and return your verdict.",
    "provider": "anthropic",
    "model": "claude-opus-4-6",
    "temperature": 0,
    "maxTokens": 500,
    "schema": {
      "type": "object",
      "properties": {
        "approved": {"type": "boolean", "description": "true if all critical checks pass"},
        "errors": {"type": "array", "items": {"type": "string"}, "description": "Specific errors found. Empty if approved."},
        "warnings": {"type": "array", "items": {"type": "string"}, "description": "Non-blocking concerns."},
        "summary": {"type": "string", "description": "One-line verdict"}
      },
      "required": ["approved", "errors", "summary"]
    }
  }')

# Set gateway URL if not already set
export OPENCLAW_URL="${OPENCLAW_URL:-http://localhost:18789}"

openclaw.invoke --tool llm-task --action json --args-json "$ARGS_JSON"

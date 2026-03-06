#!/bin/bash

# verify-email-params.sh — Pre-flight check for email send parameters
#
# Catches the top recurring mistakes BEFORE the gog send command runs.
# Run this, fix any errors, THEN run gog send.
#
# USAGE:
#   verify-email-params.sh \
#     --is-reply true \
#     --message-id "19cbff105304bf97" \
#     --subject "RE: Friday data call recap" \
#     --body-html "<div style=\"font-size:18px\"><p>Thanks...</p></div>" \
#     --cc "daver@mindfireinc.com" \
#     --has-reply-all true
#
# EXIT CODES:
#   0 = all checks pass
#   1 = one or more errors found (DO NOT SEND)

set -euo pipefail

# Parse args
IS_REPLY=""
MESSAGE_ID=""
SUBJECT=""
BODY_HTML=""
CC=""
HAS_REPLY_ALL=""
USES_BODY_FLAG=""

while [[ $# -gt 0 ]]; do
  case $1 in
    --is-reply) IS_REPLY="$2"; shift 2 ;;
    --message-id) MESSAGE_ID="$2"; shift 2 ;;
    --subject) SUBJECT="$2"; shift 2 ;;
    --body-html) BODY_HTML="$2"; shift 2 ;;
    --cc) CC="$2"; shift 2 ;;
    --has-reply-all) HAS_REPLY_ALL="$2"; shift 2 ;;
    --uses-body-flag) USES_BODY_FLAG="$2"; shift 2 ;;
    *) echo "Unknown arg: $1"; exit 1 ;;
  esac
done

ERRORS=()
WARNINGS=()

# ── CHECK 1: --body vs --body-html ──
if [[ "$USES_BODY_FLAG" == "true" ]]; then
  ERRORS+=("❌ Using --body instead of --body-html. This causes tiny font. Change to --body-html.")
fi

# ── CHECK 2: HTML wrapper ──
if [[ -n "$BODY_HTML" ]]; then
  if ! echo "$BODY_HTML" | grep -q 'font-size'; then
    ERRORS+=("❌ Body missing font-size wrapper. Must start with <div style=\"font-size:18px\">")
  fi
fi

# ── CHECK 3: Signature ──
if [[ -n "$BODY_HTML" ]]; then
  if ! echo "$BODY_HTML" | grep -q 'Amber Ives<br>MindFire, Inc.'; then
    ERRORS+=("❌ Signature wrong or missing. Must be exactly: Amber Ives<br>MindFire, Inc.")
  fi
  # Check for bad signature additions
  if echo "$BODY_HTML" | grep -qi 'Assistant to'; then
    ERRORS+=("❌ Signature contains 'Assistant to' — remove it. Just name and company.")
  fi
fi

# ── CHECK 4: Reply threading ──
if [[ "$IS_REPLY" == "true" ]]; then
  if [[ -z "$MESSAGE_ID" ]]; then
    ERRORS+=("❌ REPLY without message_id! You MUST use --reply-to-message-id, not --to. Go re-read the email to get the messageId.")
  fi
  if [[ "$HAS_REPLY_ALL" != "true" ]]; then
    ERRORS+=("❌ REPLY without --reply-all. CC recipients will be dropped.")
  fi
  if [[ -n "$SUBJECT" ]] && ! echo "$SUBJECT" | grep -qi '^RE:'; then
    WARNINGS+=("⚠️  Reply subject doesn't start with 'RE:' — is this intentional?")
  fi
fi

# ── CHECK 5: CC Dave ──
if [[ "$IS_REPLY" != "true" ]] && [[ -n "$CC" ]]; then
  if ! echo "$CC" | grep -qi 'daver@mindfireinc.com'; then
    WARNINGS+=("⚠️  Dave (daver@mindfireinc.com) not in CC for new email — is this intentional?")
  fi
fi

# ── CHECK 6: Empty body ──
if [[ -z "$BODY_HTML" ]]; then
  ERRORS+=("❌ Body is empty!")
fi

# ── REPORT ──
echo ""
if [[ ${#ERRORS[@]} -eq 0 ]] && [[ ${#WARNINGS[@]} -eq 0 ]]; then
  echo "✅ ALL CHECKS PASSED — safe to send."
  exit 0
fi

if [[ ${#ERRORS[@]} -gt 0 ]]; then
  echo "🚫 VERIFICATION FAILED — DO NOT SEND"
  echo ""
  for err in "${ERRORS[@]}"; do
    echo "  $err"
  done
fi

if [[ ${#WARNINGS[@]} -gt 0 ]]; then
  echo ""
  echo "Warnings (review but may be OK):"
  for warn in "${WARNINGS[@]}"; do
    echo "  $warn"
  done
fi

if [[ ${#ERRORS[@]} -gt 0 ]]; then
  echo ""
  echo "Fix the errors above, then re-run verification."
  exit 1
fi

exit 0

# email-send.lobster
# Verified email send with Opus 4.6 pre-flight validation.
#
# WHY THIS EXISTS: Amber (running Sonnet) repeatedly makes the same
# email mistakes — using --to instead of --reply-to-message-id, dropping
# CC recipients, using --body instead of --body-html. Doc-level
# instructions don't reliably prevent these errors (see Lesson #8).
#
# This workflow adds an Opus 4.6 verifier step between "draft approved"
# and "command executed." Opus reviews the send parameters against the
# original email headers and catches mistakes before they reach inboxes.
#
# ARCHITECTURE (2026-03-05 rewrite — see Lesson #13):
#   Lobster child processes run in /bin/sh and bypass OpenClaw's
#   exec-approval pipeline. So we can't rely on exec-approval as a gate
#   inside the workflow. Instead:
#   - Dave approves the DRAFT content via Telegram (step 6 in SKILL.md)
#   - Opus verifies the TECHNICAL correctness (step 1 below)
#   - Send uses gog-real (hard copy in trusted scripts dir) — no approval
#   - This is safe because Dave already approved + Opus already verified
#
# FLOW:
#   1. verify-email-send.sh calls Opus via openclaw.invoke → llm-task
#   2. If FAIL → workflow stops, Amber sees specific errors to fix
#   3. If PASS → gog-real sends the email (auto-approved, trusted dir)
#   4. After send succeeds → auto-tag thread as Handled
#
# REQUIRES:
#   - Gateway running (openclaw.invoke connects to it via OPENCLAW_URL)
#   - llm-task plugin enabled with claude-opus-4-6 in allowedModels
#   - gog-real hard copy in scripts dir (not a symlink — see Lesson #9)
#   - jq installed (for safe JSON construction in verify script)
#
# USAGE (from Amber's session):
#   lobster run /Users/amberives/.openclaw/workspace/workflows/email-send.lobster \
#     --arg original_from="Alex Fechner <AFechner@advprinting.com>" \
#     --arg original_to="David Rosendahl <daver@mindfireinc.com>" \
#     --arg original_cc="Bryan Beelek <bbeelek@advprinting.com>, Dan Tissi <DTissi@advprinting.com>" \
#     --arg message_id="19cbff105304bf97" \
#     --arg thread_id="19cbf0a3d6e227b1" \
#     --arg subject="RE: Friday data call recap" \
#     --arg body_html="<div style=\"font-size:18px\"><p>Thanks Alex...</p><p>Amber Ives<br>MindFire, Inc.</p></div>" \
#     --arg is_reply="true"

name: email-send
description: Opus-verified email send — catches threading, CC, and format errors before sending

args:
  original_from: {}
  original_to: {}
  original_cc: { default: "" }
  message_id: {}
  thread_id: {}
  subject: {}
  body_html: {}
  is_reply: { default: "true" }

steps:
  # ──────────────────────────────────────────────
  # STEP 1: Opus 4.6 verifies the send parameters
  # Uses a standalone script for safe quoting of HTML args.
  # openclaw.invoke routes through the Gateway to call llm-task.
  # ──────────────────────────────────────────────
  - id: verify
    env:
      OPENCLAW_URL: "http://localhost:18789"
      PATH: "/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin"
    command: >
      /Users/amberives/.openclaw/workspace/scripts/verify-email-send.sh

  # ──────────────────────────────────────────────
  # STEP 2: HALT if verification failed
  # ──────────────────────────────────────────────
  - id: report-failure
    command: |
      echo "🚫 OPUS VERIFICATION FAILED"
      echo ""
      echo "Errors found:"
      echo '$verify.stdout' | jq -r '.errors[]' 2>/dev/null || echo "(could not parse errors)"
      echo ""
      echo "Summary: $(echo '$verify.stdout' | jq -r '.summary' 2>/dev/null || echo 'unknown')"
      echo ""
      echo "Fix these issues and re-run the workflow."
      echo "DO NOT send the email until all checks pass."
    condition: $verify.json.approved == false

  # ──────────────────────────────────────────────
  # STEP 3: Execute send (only if Opus verified)
  # Uses gog-real (hard copy in trusted scripts dir).
  # Lobster child processes bypass exec-approval, so this
  # runs directly. Safety relies on:
  #   - Dave already approved the draft content (SKILL.md step 6)
  #   - Opus already verified technical correctness (step 1)
  # ──────────────────────────────────────────────
  - id: send-reply
    env:
      MSG_ID: "$LOBSTER_ARG_MESSAGE_ID"
      SUBJECT: "$LOBSTER_ARG_SUBJECT"
      BODY_HTML: "$LOBSTER_ARG_BODY_HTML"
    command: |
      /Users/amberives/.openclaw/workspace/scripts/gog-real gmail send \
        --reply-to-message-id "$MSG_ID" \
        --reply-all \
        --cc daver@mindfireinc.com \
        --subject "$SUBJECT" \
        --body-html "$BODY_HTML"
    condition: $verify.json.approved == true

  # ──────────────────────────────────────────────
  # STEP 4: Tag thread as Handled (only after send succeeds)
  # ──────────────────────────────────────────────
  - id: tag-handled
    env:
      THREAD_ID: "$LOBSTER_ARG_THREAD_ID"
    command: |
      /Users/amberives/.openclaw/workspace/scripts/gog-email-tag.sh \
        gmail thread modify "$THREAD_ID" \
        --add "Handled" --remove "UNREAD" --force
    condition: $send-reply.exitCode == 0

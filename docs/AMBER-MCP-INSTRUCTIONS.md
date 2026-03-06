# Amber: MCP Migration Instructions

**Date:** 2026-03-06
**What this does:** Replaces your gog CLI wrappers with native MCP tool calls for email and calendar.
**Branch:** `phase1-mcp-migration` (main is untouched)

---

## What You Need From Dave (ONE thing)

Before you can run the setup, Dave needs to provide two values:

- `GOOGLE_OAUTH_CLIENT_ID`
- `GOOGLE_OAUTH_CLIENT_SECRET`

These come from Google Cloud Console. If gog already has OAuth configured on your machine, check if you can reuse those credentials:

```bash
gog auth status
```

If that shows a working OAuth config, Dave may already have the Client ID and Secret from the original gog setup. Ask him.

**You also need Dave present for ONE click:** The OAuth consent screen will open in a browser. Someone needs to click "Authorize" as aives@mindfiremail.info. This happens once and takes 5 seconds.

---

## Step 1: Pull the branch

```bash
cd ~/.openclaw/workspace
git fetch origin
git checkout phase1-mcp-migration
git pull origin phase1-mcp-migration
```

## Step 2: Run the setup script

Once Dave has given you the OAuth credentials:

```bash
export GOOGLE_OAUTH_CLIENT_ID="<paste-from-dave>"
export GOOGLE_OAUTH_CLIENT_SECRET="<paste-from-dave>"
cd ~/.openclaw/workspace
./scripts/mcp-migrate-phase1.sh setup
```

The script will:
1. Check prerequisites (Node.js, Python, npm, OpenClaw)
2. Install google-workspace-mcp via uvx
3. Add OAuth env vars to your ~/.zshrc
4. **Open a browser for OAuth** — Dave clicks Authorize (the ONE manual step)
5. Register the MCP server in ~/.openclaw/openclaw.json
6. Install ClawBands + apply the security policy
7. Restart the gateway
8. Verify everything is connected

## Step 3: Run read tests

```bash
./scripts/mcp-migrate-phase1.sh test
```

This tests search, labels, calendar — all read-only, all auto-approved. No Telegram prompts should appear.

## Step 4: Test send (needs Dave on Telegram)

Once reads work, test a send. In your OpenClaw session, call:

```
send_gmail_message(
  to="daver@mindfireinc.com",
  subject="MCP Test Email",
  body="<div style='font-size:18px'><p>This is a test email sent via MCP. If you received this, Phase 1 email sending works.</p><p>Best,</p><p>Amber Ives<br>MindFire, Inc.</p></div>",
  body_format="html",
  user_google_email="aives@mindfiremail.info"
)
```

**Expected:** ClawBands intercepts this, sends a YES/NO prompt to Dave on Telegram. Dave approves. Email sends.

## Step 5: Test reply threading (MOST CRITICAL)

This is the biggest behavioral change. MCP has NO `--reply-all` flag.

1. Have Dave send a test email to aives@mindfiremail.info with a CC recipient
2. Read the email. Capture: messageId, threadId, ALL To recipients, ALL CC recipients, Message-ID header
3. Reply using MCP:

```
send_gmail_message(
  to="<original-sender-email>",
  cc="daver@mindfireinc.com,<other-cc-recipients>",
  subject="RE: <original-subject>",
  body="<div style='font-size:18px'><p>Test reply via MCP.</p><p>Best,</p><p>Amber Ives<br>MindFire, Inc.</p></div>",
  body_format="html",
  thread_id="<threadId>",
  in_reply_to="<messageId>",
  references="<Message-ID-header>",
  user_google_email="aives@mindfiremail.info"
)
```

4. **Verify in Gmail web:** Does the reply appear IN the thread? Are all recipients included? Is the HTML correct?

## Step 6: Test calendar create (needs Dave on Telegram)

```
create_event(
  calendar_id="daver@mindfireinc.com",
  summary="MCP Test Event — DELETE ME",
  start="2026-03-07T15:00:00",
  end="2026-03-07T15:30:00",
  description="Test event from MCP migration. Safe to delete."
)
```

**Expected:** ClawBands intercepts, Dave approves via Telegram. Then delete the test event in Google Calendar.

## Step 7: Switch skill files (ONLY after ALL tests pass)

```bash
cd ~/.openclaw/workspace

# Back up originals
cp skills/email-read/SKILL.md skills/email-read/SKILL-gog-backup.md
cp skills/email-send/SKILL.md skills/email-send/SKILL-gog-backup.md
cp skills/calendar-read/SKILL.md skills/calendar-read/SKILL-gog-backup.md
cp skills/calendar-create/SKILL.md skills/calendar-create/SKILL-gog-backup.md

# Switch to MCP versions
cp skills/email-read/SKILL-MCP.md skills/email-read/SKILL.md
cp skills/email-send/SKILL-MCP.md skills/email-send/SKILL.md
cp skills/calendar-read/SKILL-MCP.md skills/calendar-read/SKILL.md
cp skills/calendar-create/SKILL-MCP.md skills/calendar-create/SKILL.md
```

Then restart your session so the new SKILL.md files load into your system prompt.

## Step 8: Check status anytime

```bash
./scripts/mcp-migrate-phase1.sh status
```

## If Something Breaks

```bash
./scripts/mcp-migrate-phase1.sh rollback
```

This disables the MCP server in openclaw.json, restores gog-based SKILL.md files, and restarts the gateway. The gog CLI was never removed — it still works as a fallback.

The git tag `baseline-email-working-2026-03-06` marks the exact state where email was working with gog wrappers.

---

## Summary: What Needs a Human vs What Amber Can Do

| Step | Who | Notes |
|------|-----|-------|
| Provide OAuth credentials | Dave | One-time, before setup |
| Click OAuth "Authorize" in browser | Dave (5 seconds) | One-time, during setup |
| Run setup script | Amber | `./scripts/mcp-migrate-phase1.sh setup` |
| Run read tests | Amber | `./scripts/mcp-migrate-phase1.sh test` |
| Approve test send via Telegram | Dave | Normal approval flow |
| Run send/reply/calendar tests | Amber | Through OpenClaw session |
| Switch skill files | Amber | Copy commands in Step 7 |
| Rollback if needed | Amber | `./scripts/mcp-migrate-phase1.sh rollback` |

# MCP Migration Guide — Phase 1: Gmail & Calendar

**Date:** 2026-03-06
**Purpose:** Replace gog CLI binary wrappers with google-workspace-mcp server + ClawBands middleware
**Baseline:** Commit `4d3cb8f` / tag `baseline-email-working-2026-03-06` (current email system working)

---

## Quick Start (Automated)

Most of the setup is automated via a script. On Amber's machine:

```bash
# 1. Dave provides OAuth credentials
export GOOGLE_OAUTH_CLIENT_ID="<from Google Cloud Console>"
export GOOGLE_OAUTH_CLIENT_SECRET="<from Google Cloud Console>"

# 2. Run the setup script (Parts A-C automated)
./scripts/mcp-migrate-phase1.sh setup

# 3. Run read tests (Part D automated reads)
./scripts/mcp-migrate-phase1.sh test

# 4. Check status anytime
./scripts/mcp-migrate-phase1.sh status

# 5. Rollback if anything breaks
./scripts/mcp-migrate-phase1.sh rollback
```

**The ONE manual step:** Dave clicks "Authorize" in the browser during OAuth setup (5 seconds, one time only).

For Amber-specific instructions, see: `docs/AMBER-MCP-INSTRUCTIONS.md`

The detailed manual steps are below for reference.

---

## Overview

This guide walks through replacing the gog binary wrapper approach with MCP-native tool calls. After completion:
- Email reads use `search_gmail_messages` / `get_gmail_message_content` (auto-approved via ClawBands)
- Email sends use `send_gmail_message` (approved via ClawBands → Telegram prompt)
- Calendar reads use `get_events` / `list_calendars` (auto-approved)
- Calendar creates use `create_event` (approved via ClawBands → Telegram prompt)
- No more gog wrappers, PATH hacking, or exec-approvals.json surgery

## What This Replaces

| Current (gog CLI) | New (MCP) | Approval |
|---|---|---|
| `gog-email-read.sh gmail messages search` | `search_gmail_messages` | ALLOW (auto) |
| `gog-email-read.sh gmail messages get` | `get_gmail_message_content` | ALLOW (auto) |
| `gog-email-read.sh gmail thread get` | `get_gmail_thread_content` | ALLOW (auto) |
| `gog-email-read.sh gmail labels list` | `list_gmail_labels` | ALLOW (auto) |
| `gog-email-tag.sh gmail thread modify` | `modify_gmail_message_labels` | ALLOW (auto) |
| `/usr/local/bin/gog gmail send` | `send_gmail_message` | ASK (Telegram) |
| `gog-cal-read.sh cal events` | `get_events` | ALLOW (auto) |
| `gog-cal-read.sh cal list` | `list_calendars` | ALLOW (auto) |
| `gog cal create` | `create_event` | ASK (Telegram) |
| exec-approvals.json | ClawBands policy.json | — |

## What Does NOT Change

- SOUL.md, MEMORY.md, AGENTS.md — personality, memory, agent roles
- Telegram channel — Dave's command channel
- Approval pattern — reads auto, sends to Dave (same concept, cleaner implementation)
- Verify-with-Opus — keep verify-with-opus.sh, adapt verify-prompts for new param names
- Follow-up tracker, relationship manager, heartbeat — all unchanged
- Git workflow — Claude Code pushes, Amber pulls via update-self.sh

---

## Prerequisites

Before starting:
- [ ] Current email system confirmed working (baseline tag exists)
- [ ] Amber's machine has: Node.js >= 18, Python 3.10+, OpenClaw running
- [ ] Dave has Google Cloud Console access for OAuth credentials
- [ ] This branch (`phase1-mcp-migration`) pulled to Amber's machine

---

## Part A: Install google-workspace-mcp

### A1. Create Google Cloud OAuth Credentials

1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Create or select a project (can reuse existing one if gog already has OAuth)
3. Enable these APIs:
   - Gmail API
   - Google Calendar API
4. Go to **Credentials** → **Create Credentials** → **OAuth 2.0 Client ID**
5. Application type: **Desktop application**
6. Download the credentials — note the `CLIENT_ID` and `CLIENT_SECRET`

> **Note:** If gog already has OAuth configured, you may be able to reuse the same Client ID and Client Secret. Check `gog auth status` or the existing OAuth config.

### A2. Install the MCP Server

```bash
# Option 1: via uvx (recommended)
pip install uv  # if not installed
uvx workspace-mcp

# Option 2: via pip
pip install workspace-mcp
```

### A3. Set Environment Variables

Add to Amber's shell profile (`~/.zshrc` or `~/.bashrc`):

```bash
export GOOGLE_OAUTH_CLIENT_ID="<from step A1>"
export GOOGLE_OAUTH_CLIENT_SECRET="<from step A1>"
export USER_GOOGLE_EMAIL="aives@mindfiremail.info"
```

Source the profile: `source ~/.zshrc`

### A4. Run Initial Auth Flow

```bash
uvx workspace-mcp --tools gmail calendar
# Follow the OAuth flow in browser
# Authorize as aives@mindfiremail.info
# Token will be cached locally
```

### A5. Verify MCP Server Works Standalone

```bash
# Quick test — list Gmail labels
echo '{"method": "tools/call", "params": {"name": "list_gmail_labels", "arguments": {"user_google_email": "aives@mindfiremail.info"}}}' | uvx workspace-mcp --tools gmail
```

---

## Part B: Register MCP Server in OpenClaw

### B1. Update openclaw.json

Add the MCP server configuration. The template is in `config/mcp-servers.json` — copy the values:

```json
{
  "mcpServers": {
    "google-workspace": {
      "command": "uvx",
      "args": ["workspace-mcp", "--tools", "gmail", "calendar"],
      "env": {
        "GOOGLE_OAUTH_CLIENT_ID": "<your-client-id>",
        "GOOGLE_OAUTH_CLIENT_SECRET": "<your-client-secret>",
        "USER_GOOGLE_EMAIL": "aives@mindfiremail.info"
      }
    }
  }
}
```

Merge this into the existing `mcpServers` section of `~/.openclaw/openclaw.json`.

### B2. Restart Gateway

```bash
openclaw gateway restart
```

### B3. Verify MCP Tools Are Available

```bash
openclaw tools list
# Should show: search_gmail_messages, get_gmail_message_content,
# get_gmail_thread_content, send_gmail_message, list_gmail_labels,
# modify_gmail_message_labels, get_events, create_event, etc.
```

---

## Part C: Install ClawBands

### C1. Install

```bash
npm install -g clawbands
clawbands init  # Interactive wizard — accept defaults
```

### C2. Apply Policy

Copy the prepared policy template:

```bash
cp /Users/amberives/.openclaw/workspace/config/clawbands-policy.json ~/.openclaw/clawbands/policy.json
```

Or on Dave's machine, push the config and have Amber pull it.

### C3. Restart Gateway

```bash
openclaw gateway restart
```

### C4. Verify ClawBands Is Active

```bash
clawbands status
# Should show: active, policy loaded, Telegram approval channel configured
```

---

## Part D: Test Suite (DO NOT SKIP)

### D1. Test Read Operations (should auto-approve, no Telegram prompt)

```
# In Amber's Telegram session:
search_gmail_messages(query="is:unread -label:Handled", max_results=5, user_google_email="aives@mindfiremail.info")

# Expected: Returns email list. No approval prompt.
```

```
get_gmail_message_content(message_id="<known-messageId>", user_google_email="aives@mindfiremail.info")

# Expected: Returns full email content. No approval prompt.
```

```
get_events(calendar_id="daver@mindfireinc.com", time_min="2026-03-06T00:00:00", time_max="2026-03-06T23:59:59")

# Expected: Returns today's events. No approval prompt.
```

### D2. Test Write Operations (should prompt Dave via Telegram)

```
send_gmail_message(
  to="daver@mindfireinc.com",
  subject="MCP Test Email",
  body="<div style='font-size:18px'><p>This is a test email sent via MCP. If you received this, Phase 1 email sending works.</p><p>Best,</p><p>Amber Ives<br>MindFire, Inc.</p></div>",
  body_format="html",
  user_google_email="aives@mindfiremail.info"
)

# Expected: ClawBands intercepts, sends YES/NO prompt to Dave on Telegram.
# Dave approves → email sends.
```

### D3. Test Reply Threading (CRITICAL)

This is the most important test. The MCP server has NO `--reply-all` flag.

1. Have Dave send a test email to aives@mindfiremail.info with a CC recipient
2. Read the email, capture: `messageId`, `threadId`, all To+CC recipients
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
  references="<messageId>",
  user_google_email="aives@mindfiremail.info"
)
```

4. **Verify in Gmail web:**
   - Does the reply appear IN the thread (not as a new standalone email)?
   - Are all original recipients included?
   - Is the HTML rendering correctly (18px font)?

### D4. Test Calendar Create (should prompt Dave)

```
create_event(
  calendar_id="daver@mindfireinc.com",
  summary="MCP Test Event — DELETE ME",
  start="2026-03-07T15:00:00",
  end="2026-03-07T15:30:00",
  description="Test event from MCP migration. Safe to delete."
)

# Expected: ClawBands intercepts, Dave approves via Telegram.
# Then delete the test event manually in Google Calendar.
```

---

## Part E: Switch Skill Files

After ALL tests pass:

### E1. Update Skill Files

For each skill, replace the gog commands with MCP tool calls. The `SKILL-MCP.md` files in each skill directory have the complete MCP versions ready to go.

```bash
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

### E2. Update AGENTS.md Tool References

Update any references to gog commands in AGENTS.md to reference MCP tool names.

### E3. Commit and Push

```bash
git add -A && git commit -m "Switch to MCP-native skill files" && git push
```

### E4. Pull on Amber's Machine

```bash
./update-self.sh
```

### E5. Restart Amber's Session

Restart so the new SKILL.md files are loaded into the system prompt.

---

## Part F: Cleanup (ONLY after confirming MCP works in production)

Wait at least 24-48 hours of successful MCP operation before cleanup.

1. Remove from exec-approvals.json: all gog-related entries
2. Archive (don't delete): `gog-email-read.sh`, `gog-cal-read.sh`, `gog-email-tag.sh`, `gog` wrapper
3. **Keep `gog-real` as emergency fallback** — do NOT delete
4. Archive the `SKILL-gog-backup.md` files

---

## Rollback Plan

If anything breaks after switching to MCP:

```bash
# On Dave's dev machine:
git checkout main  # Return to pre-MCP state

# On Amber's machine:
./update-self.sh  # Restores gog-based SKILL.md files

# Disable MCP server:
# Edit ~/.openclaw/openclaw.json — set "disabled": true on google-workspace entry
openclaw gateway restart

# gog CLI still works — it was never removed
```

The baseline tag `baseline-email-working-2026-03-06` marks the exact commit where email was confirmed working with gog wrappers.

---

## Key Behavioral Change: No Reply-All Flag

**This is the single most important thing to understand about the MCP migration.**

With gog: `--reply-all` automatically includes all original To and CC recipients.

With MCP: There is no `--reply-all`. Amber must:
1. When **reading** an email, capture the **complete recipient list** (From, To, CC)
2. When **replying**, explicitly list all recipients in `to` and `cc` parameters
3. Use `thread_id` + `in_reply_to` + `references` for threading

The `SKILL-MCP.md` files have been updated to emphasize this, but it's a behavioral change that needs monitoring during the first few days.

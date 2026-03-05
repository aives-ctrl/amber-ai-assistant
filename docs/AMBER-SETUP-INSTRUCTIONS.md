# Amber Setup Instructions (March 2026 Architecture Overhaul)

These are machine-specific changes that must be run on Amber's machine. They cannot be managed via the git repo.

Run these in order. Each section builds on the previous.

---

## STEP 1: Pull latest config from git

```bash
cd ~/.openclaw/workspace && git pull origin main
```

Verify new files exist:
```bash
ls skills/
ls workflows/
```

You should see: `email-read/`, `email-send/`, `calendar-read/`, `calendar-create/`, `startup/` in skills, and `email-triage.lobster.yaml` in workflows.

---

## STEP 2: Fix the exec allowlist (glob patterns + shell tools)

First, clear any broken entries:
```bash
openclaw approvals allowlist list
```

Remove any entries that point to wrong paths or the raw `gog` binary:
```bash
openclaw approvals allowlist remove "<wrong-path>"
```

Then add the correct entries with globs:
```bash
openclaw approvals allowlist add "/Users/amberives/.openclaw/workspace/scripts/gog-*"
openclaw approvals allowlist add "/usr/local/bin/gog-email-read.sh"
openclaw approvals allowlist add "/usr/local/bin/gog-cal-read.sh"
```

Add basic shell tools so grep/cat/ls stop triggering approval:
```bash
openclaw approvals allowlist add "/usr/bin/grep"
openclaw approvals allowlist add "/usr/bin/cat"
openclaw approvals allowlist add "/usr/bin/ls"
openclaw approvals allowlist add "/usr/bin/python3"
openclaw approvals allowlist add "/opt/homebrew/bin/grep"
```

Verify:
```bash
openclaw approvals allowlist list
```

Should show wrapper script globs + shell tools. Should NOT show raw `/usr/local/bin/gog`.

---

## STEP 3: Configure approval channel separation (PREVENTS SELF-APPROVAL)

Find Dave's personal Telegram chat ID:
```bash
openclaw sessions list
```

Look for Dave's Telegram session key. It will contain his chat ID.

Then set approvals to route to Dave's PRIVATE chat:
```bash
openclaw config set approvals.exec.targets '[{"channel": "telegram", "to": "<DAVE_PERSONAL_CHAT_ID>"}]'
```

Replace `<DAVE_PERSONAL_CHAT_ID>` with the actual numeric ID.

This means:
- Amber converses in her regular channel
- Approval prompts go ONLY to Dave's private DM with the bot
- Amber cannot self-approve (she can't post in Dave's private chat)

---

## STEP 4: Configure safe bins (shell tool approvals)

```bash
openclaw config set tools.exec.safeBinTrustedDirs '["/bin", "/usr/bin", "/opt/homebrew/bin"]'
```

---

## STEP 5: Apply cost control settings

```bash
openclaw config set session.pruning.mode cache-ttl
openclaw config set session.pruning.ttl 5m
openclaw config set session.contextTokens 50000
openclaw config set model.caching true
```

---

## STEP 6: Install telegram-approval-buttons plugin (if not already installed)

```bash
openclaw plugins install telegram-approval-buttons
```

Verify it's configured with the bot token and chat ID:
```bash
openclaw plugins list
```

---

## STEP 7: Restart gateway and test

```bash
openclaw doctor
openclaw gateway restart
```

After restart, test:

**Test 1 - Read (should NOT trigger approval):**
```bash
/Users/amberives/.openclaw/workspace/scripts/gog-email-read.sh gmail labels list
```

**Test 2 - Send (SHOULD trigger approval in Dave's private chat):**
```bash
gog gmail send --to "test@example.com" --subject "test" --body-html "<p>test</p>"
```
(Cancel this after verifying the approval fires in Dave's private chat, not Amber's channel)

**Test 3 - Grep (should NOT trigger approval):**
```bash
grep -i "test" memory/*.md
```

---

## STEP 8: Process the 25 unread email backlog

After everything is working, process the inbox:
```bash
/Users/amberives/.openclaw/workspace/scripts/gog-email-read.sh gmail messages search 'is:unread -label:Handled -from:daver@mindfireinc.com' --max 25
```

Categorize each email per HEARTBEAT.md rules. Send Dave ONE consolidated Telegram message with anything that needs his attention. Handle FYIs silently.

---

## STEP 9 (FUTURE): Gmail PubSub setup

This requires Dave to enable the Google Calendar API first. Once enabled:

```bash
gog gmail watch serve \
  --topic projects/<GCP_PROJECT>/topics/gog-gmail-watch \
  --account aives@mindfiremail.info \
  --label INBOX \
  --include-body --max-bytes 4096 \
  --hook-url http://127.0.0.1:18789/hook/gmail \
  --hook-token "$OPENCLAW_HOOK_TOKEN"
```

And configure in openclaw.json:
```json5
hooks: {
  gmail: {
    model: "anthropic/claude-sonnet-4-20250514",
    sessionKey: "email-{{messageId}}",
    channel: "last"
  }
}
```

This eliminates polling. Emails arrive in real time, pre-fetched. Heartbeat becomes backup only.

---

## Verification Summary

After completing steps 1-7, confirm:

- [ ] `skills/` directory has 5 skill folders
- [ ] `workflows/` directory has `email-triage.lobster.yaml`
- [ ] Wrapper script reads don't trigger approval
- [ ] Raw gog sends DO trigger approval
- [ ] Approval prompts arrive in Dave's PRIVATE Telegram, not Amber's channel
- [ ] grep/cat/ls don't trigger approval
- [ ] `openclaw approvals allowlist list` shows no raw `gog` entry
- [ ] Email backlog is being processed

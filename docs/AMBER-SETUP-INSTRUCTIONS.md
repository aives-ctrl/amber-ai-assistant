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

First, check current allowlist entries:
```bash
cat ~/.openclaw/exec-approvals.json
```

Remove any entries that point to wrong paths or the raw `gog` binary:
```bash
openclaw approvals allowlist remove "<wrong-path>"
```

Then add the correct entries with globs:
```bash
openclaw approvals allowlist add "/Users/amberives/.openclaw/workspace/scripts/gog-*"
```

Add basename fallbacks (catches calls without full path):
```bash
openclaw approvals allowlist add "gog-email-read.sh"
openclaw approvals allowlist add "gog-cal-read.sh"
```

**⚠️ Why both?** Amber sometimes calls `gog-email-read.sh` instead of the full path. The glob catches full-path calls, the basenames catch shorthand calls. Both are read-only wrapper scripts, so this is safe.

Add basic shell tools so grep/cat/ls stop triggering approval:
```bash
openclaw approvals allowlist add "/usr/bin/grep"
openclaw approvals allowlist add "/usr/bin/cat"
openclaw approvals allowlist add "/usr/bin/ls"
openclaw approvals allowlist add "/usr/bin/python3"
openclaw approvals allowlist add "/opt/homebrew/bin/grep"
```

Verify by checking the file directly:
```bash
cat ~/.openclaw/exec-approvals.json
```

Should show wrapper script globs + shell tools. Should NOT show raw `/usr/local/bin/gog`.

**⚠️ Note:** `openclaw approvals allowlist list` may not exist in all versions. Use `cat ~/.openclaw/exec-approvals.json` to inspect the allowlist instead.

---

## STEP 2B: Add scripts directory to PATH

The wrapper scripts (`gog-email-read.sh`, `gog-cal-read.sh`) live in the workspace scripts directory. Without this in PATH, calling them by basename fails with "command not found" even when the allowlist approves them.

```bash
echo 'export PATH="/Users/amberives/.openclaw/workspace/scripts:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

Verify it works:
```bash
which gog-email-read.sh
# Should output: /Users/amberives/.openclaw/workspace/scripts/gog-email-read.sh
```

---

## STEP 3: Configure approval channel separation (PREVENTS SELF-APPROVAL)

Route exec approvals to Dave's PRIVATE Telegram DM (chat ID `8703088279`):
```bash
openclaw config set approvals.exec.enabled true
openclaw config set approvals.exec.targets '[{"channel": "telegram", "to": "8703088279"}]'
```

This means:
- Amber converses in her regular channel
- Approval prompts go ONLY to Dave's private DM with the bot
- Amber cannot self-approve (she can't post in Dave's private chat)

---

## STEP 4: Configure safe bins (shell tool approvals)

Add trusted directories so basic shell tools AND wrapper scripts don't trigger approval:
```bash
openclaw config set tools.exec.safeBinTrustedDirs '["/bin", "/usr/bin", "/opt/homebrew/bin", "/Users/amberives/.openclaw/workspace/scripts"]'
```

**⚠️ Including the scripts directory is critical.** The exec-approval allowlist matching can fail on wrapper scripts even when paths are correct. Adding the scripts directory to `safeBinTrustedDirs` bypasses this by trusting all binaries in that directory.

---

## STEP 5: Apply cost control settings

**⚠️ The config paths are under `agents.defaults`, NOT `session`.**

```bash
openclaw config set agents.defaults.contextPruning.mode cache-ttl
openclaw config set agents.defaults.contextPruning.ttl 5m
openclaw config set agents.defaults.contextTokens 50000
```

This caps context at 50k tokens (prevents $59 sessions) and trims stale tool output after 5 minutes.

**Note:** Prompt caching (`cacheRetention`) is already configured by default — no action needed.

---

## STEP 6: Apply safety settings (REQUIRED)

Prevent skills from auto-allowlisting binaries:
```bash
openclaw config set tools.exec.autoAllowSkills false
```

**⚠️ `askFallback` cannot be set via CLI** (there is no `openclaw approvals defaults` subcommand). You must edit the file directly:

Open `~/.openclaw/exec-approvals.json` and ensure the `"defaults"` section contains `"askFallback": "deny"`:
```json
{
  "defaults": {
    "askFallback": "deny"
  }
}
```

If the `"defaults"` key doesn't exist, add it. This ensures that if the approval UI is unavailable (e.g., during gateway restart), commands are DENIED rather than auto-approved.

---

## STEP 7: Install telegram-approval-buttons plugin (if not already installed)

```bash
openclaw plugins install telegram-approval-buttons
```

Verify it's configured with the bot token and chat ID:
```bash
openclaw plugins list
```

---

## STEP 8: Restart gateway and test

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

## STEP 9: Process the 25 unread email backlog

After everything is working, process the inbox:
```bash
/Users/amberives/.openclaw/workspace/scripts/gog-email-read.sh gmail messages search 'is:unread -label:Handled -from:daver@mindfireinc.com' --max 25
```

Categorize each email per HEARTBEAT.md rules. Send Dave ONE consolidated Telegram message with anything that needs his attention. Handle FYIs silently.

---

## STEP 10 (FUTURE): Gmail PubSub setup

Google Calendar API is now enabled (2026-03-04). Remaining setup:

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

After completing steps 1-8, confirm:

- [ ] `skills/` directory has 5 skill folders
- [ ] `workflows/` directory has `email-triage.lobster.yaml`
- [ ] Wrapper script reads don't trigger approval
- [ ] Raw gog sends DO trigger approval
- [ ] Approval prompts arrive in Dave's PRIVATE Telegram, not Amber's channel
- [ ] grep/cat/ls don't trigger approval
- [ ] `cat ~/.openclaw/exec-approvals.json` shows no raw `gog` entry in allowlist
- [ ] `askFallback` is set to `"deny"` in exec-approvals.json
- [ ] Email backlog is being processed

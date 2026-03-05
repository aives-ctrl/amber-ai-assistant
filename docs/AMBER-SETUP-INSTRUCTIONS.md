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

## STEP 2: Fix the exec allowlist (MUST edit JSON directly)

**⚠️ CRITICAL: Do NOT use `openclaw approvals allowlist add` for this.** The CLI adds entries to `agents.*.allowlist` (a wildcard/fallback section), but Amber's main agent has its own explicit `agents.main.allowlist` that takes precedence. CLI-added entries in `agents.*` are never consulted for the main agent. You must edit the JSON file directly.

### 2a. Back up the file
```bash
cp ~/.openclaw/exec-approvals.json ~/.openclaw/exec-approvals.json.bak
```

### 2b. Add wrapper script entries to agents.main.allowlist

Run this Python script to surgically update the correct section:
```bash
python3 -c "
import json

with open('/Users/amberives/.openclaw/exec-approvals.json', 'r') as f:
    data = json.load(f)

main_list = data.get('agents', {}).get('main', {}).get('allowlist', [])

# Entries to add to agents.main.allowlist
entries_to_add = [
    {'id': 'gog-email-read-basename', 'pattern': 'gog-email-read.sh'},
    {'id': 'gog-cal-read-basename', 'pattern': 'gog-cal-read.sh'},
    {'id': 'gog-scripts-glob', 'pattern': '/Users/amberives/.openclaw/workspace/scripts/gog-*'},
]

existing_patterns = {e.get('pattern') for e in main_list}

for entry in entries_to_add:
    if entry['pattern'] not in existing_patterns:
        main_list.append(entry)
        print(f'Added: {entry[\"pattern\"]}')
    else:
        print(f'Already exists: {entry[\"pattern\"]}')

# SECURITY: Remove raw gog so sends still require approval
before = len(main_list)
main_list = [e for e in main_list if e.get('pattern') != '/usr/local/bin/gog']
if len(main_list) < before:
    print('Removed: /usr/local/bin/gog')

data['agents']['main']['allowlist'] = main_list

with open('/Users/amberives/.openclaw/exec-approvals.json', 'w') as f:
    json.dump(data, f, indent=2)

print('Done.')
"
```

### 2c. Verify the changes

```bash
cat ~/.openclaw/exec-approvals.json | python3 -c "
import json, sys
data = json.load(sys.stdin)
main_list = data.get('agents', {}).get('main', {}).get('allowlist', [])
print('=== agents.main.allowlist entries containing gog ===')
for e in main_list:
    if 'gog' in e.get('pattern', '').lower():
        print(f'  {e}')
print()
print('Looking for /usr/local/bin/gog (should be GONE):')
raw = [e for e in main_list if e.get('pattern') == '/usr/local/bin/gog']
print(f'  {\"FOUND (BAD!)\" if raw else \"Not found (GOOD)\"}')
"
```

Should show:
- `gog-email-read.sh` (basename) ✅
- `gog-cal-read.sh` (basename) ✅
- `/Users/amberives/.openclaw/workspace/scripts/gog-*` (glob) ✅
- `/Users/amberives/.openclaw/workspace/scripts/gog-email-read.sh` (full path, pre-existing) ✅
- `/Users/amberives/.openclaw/workspace/scripts/gog-cal-read.sh` (full path, pre-existing) ✅
- `/usr/local/bin/gog` should be GONE ✅

**⚠️ Why all three patterns?** Amber calls wrapper scripts in different ways:
- Full path: matched by the pre-existing full-path entries
- Basename (`gog-email-read.sh`): matched by the basename entries
- Glob: catches any future `gog-*.sh` scripts added to the directory

**⚠️ Security: `/usr/local/bin/gog` must NOT be in the allowlist.** Raw `gog` can send emails, modify calendars, etc. Only the read-only wrapper scripts (`gog-email-read.sh`, `gog-cal-read.sh`) should be auto-approved. Raw `gog` calls must trigger Dave's approval.

---

## STEP 2B: Always use full paths for wrapper scripts

**⚠️ The OpenClaw gateway does NOT source `~/.zshrc` or `~/.zshenv`.** Adding the scripts directory to PATH has no effect — the gateway spawns non-interactive shells that bypass all zsh init files.

**The solution:** All config files (HEARTBEAT.md, SKILL.md, etc.) must use the full path:
```
/Users/amberives/.openclaw/workspace/scripts/gog-email-read.sh
/Users/amberives/.openclaw/workspace/scripts/gog-cal-read.sh
```

**NEVER use the basename** (`gog-email-read.sh`) in any command Amber will execute. It will fail with "command not found" even when the allowlist approves it.

The allowlist still has basename entries as a safety net (in case she improvises), but all documented commands must use full paths.

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
- [ ] `cat ~/.openclaw/exec-approvals.json` shows no raw `gog` entry in **`agents.main.allowlist`**
- [ ] Basename entries (`gog-email-read.sh`, `gog-cal-read.sh`) are in **`agents.main.allowlist`** (not just `agents.*`)
- [ ] `askFallback` is set to `"deny"` in exec-approvals.json
- [ ] Email backlog is being processed

### Troubleshooting: Allowlist entries not working

If wrapper scripts still trigger approval after adding entries:

1. **Check which section the entry is in.** `openclaw approvals allowlist add` puts entries in `agents.*.allowlist`. If `agents.main.allowlist` exists, it takes precedence and `agents.*` is ignored. Edit the JSON directly to add entries to `agents.main.allowlist`.

2. **Check `safeBinTrustedDirs`.** Run `openclaw config get tools.exec.safeBinTrustedDirs` — the scripts directory should be listed. This provides a second path for approval bypass.

3. **Check PATH.** Run `which gog-email-read.sh` — should resolve to the full path. If "not found", the scripts directory isn't in PATH (see Step 2B).

4. **Always restart gateway** after JSON edits: `openclaw gateway restart`

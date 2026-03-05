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
    {'id': 'gog-email-tag-basename', 'pattern': 'gog-email-tag.sh'},
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
- `gog-email-tag.sh` (basename) ✅
- `/Users/amberives/.openclaw/workspace/scripts/gog-*` (glob) ✅
- `/Users/amberives/.openclaw/workspace/scripts/gog-email-read.sh` (full path, pre-existing) ✅
- `/Users/amberives/.openclaw/workspace/scripts/gog-cal-read.sh` (full path, pre-existing) ✅
- `/usr/local/bin/gog` should be GONE ✅

**⚠️ Why all three patterns?** Amber calls wrapper scripts in different ways:
- Full path: matched by the pre-existing full-path entries
- Basename (`gog-email-read.sh`): matched by the basename entries
- Glob: catches any future `gog-*.sh` scripts added to the directory

**⚠️ Security: `/usr/local/bin/gog` must NOT be in the allowlist.** Raw `gog` can send emails, modify calendars, etc. Only the safe wrapper scripts (`gog-email-read.sh`, `gog-cal-read.sh`, `gog-email-tag.sh`) should be auto-approved. Raw `gog` calls must trigger Dave's approval.

**Wrapper script summary:**
| Script | Purpose | Safe? |
|--------|---------|-------|
| `gog-email-read.sh` | Read-only email ops (search, get, labels) | ✅ Auto-approved |
| `gog-cal-read.sh` | Read-only calendar ops (events, get, list) | ✅ Auto-approved |
| `gog-email-tag.sh` | Thread labeling only (add/remove labels) | ✅ Auto-approved |
| `/usr/local/bin/gog` | Direct binary — send, reply, create | ❌ Requires approval |

---

## STEP 2B: Install the gog-guard plugin (STRUCTURAL ENFORCEMENT)

**⚠️ Why this exists:** Amber's agent sometimes calls raw `gog` instead of the wrapper scripts, despite instructions in config files. This is a known OpenClaw community issue — prompt-level enforcement is unreliable. The `gog-guard` plugin provides **structural** enforcement using the `before_tool_call` hook: even when she uses raw `gog`, the plugin rewrites read/tag commands to use the allowlisted wrapper scripts before the approval check runs.

### How it works
1. Plugin lives in the repo at `plugins/gog-guard/` (index.js + openclaw.plugin.json)
2. It hooks into `before_tool_call` — fires before every tool execution
3. When Amber runs `gog gmail messages search ...`, the plugin rewrites the command to `/Users/amberives/.openclaw/workspace/scripts/gog-email-read.sh gmail messages search ...`
4. The rewritten command uses the wrapper script path → allowlisted → auto-approved
5. When she runs `gog gmail send ...`, the plugin does NOT rewrite → resolves to `/usr/local/bin/gog` → NOT in allowlist → triggers exec-approval

### Pattern routing
| Command pattern | Routed to | Approval? |
|----------------|-----------|-----------|
| `gog gmail messages search/get/list` | `gog-email-read.sh` | ✅ Auto-approved |
| `gog gmail threads get/list` | `gog-email-read.sh` | ✅ Auto-approved |
| `gog gmail labels list/get` | `gog-email-read.sh` | ✅ Auto-approved |
| `gog gmail threads modify` | `gog-email-tag.sh` | ✅ Auto-approved |
| `gog cal events/get/list` | `gog-cal-read.sh` | ✅ Auto-approved |
| `gog gmail send` | Unchanged (hits `/usr/local/bin/gog`) | ❌ Requires approval |
| `gog cal create` | Unchanged (hits `/usr/local/bin/gog`) | ❌ Requires approval |

### Install commands
```bash
# 1. Pull latest repo (plugin is at plugins/gog-guard/)
cd ~/.openclaw/workspace && git pull origin main

# 2. Symlink the plugin into OpenClaw's extensions directory
# (There is NO `openclaw plugins link` command — use a symlink instead)
ln -sf ~/.openclaw/workspace/plugins/gog-guard ~/.openclaw/extensions/gog-guard

# 3. Restart gateway to load the plugin
openclaw gateway restart

# 4. Verify plugin is loaded
openclaw plugins list
# Should show: gog-guard — "Gog Command Guard"
```

### Verify
```bash
# After gateway restart (Step 8), test:
# Read operation — should NOT trigger approval
gog gmail labels list

# Send operation — SHOULD trigger approval
gog gmail send --to "test@example.com" --subject "test" --body-html "<p>test</p>"
# (Cancel after verifying approval fires)
```

### Updating the plugin
The plugin lives in the git repo. After pulling updates:
```bash
cd ~/.openclaw/workspace && git pull origin main
openclaw gateway restart
```
No re-copy needed — the symlink points to the repo copy, so `git pull` updates the plugin in place.

---

## STEP 2C: Install the gog PATH wrapper (PRIMARY STRUCTURAL ENFORCEMENT)

**⚠️ This is the fix that actually works.** The plugin (Step 2B) has reliability issues loading. This PATH wrapper achieves the same result at the shell level — simpler and more reliable.

### Why this exists

Amber's LLM repeatedly generates bare `gog` commands for email reads despite docs saying to use `gog-email-read.sh`. This is a training-data pattern that doc-level instructions cannot override. We tried:
1. Updating skill docs 4+ times → she still uses bare `gog`
2. Multiple session restarts with fresh context → same result
3. The `gog-guard` plugin (Step 2B) → plugin loader is unreliable

The PATH wrapper is a bash script called `gog` that sits in the scripts directory. When that directory is in PATH *before* `/usr/local/bin`, it intercepts all `gog` calls. Because the scripts directory is in `safeBinTrustedDirs`, the wrapper auto-approves. For safe reads, the wrapper calls `gog-real` (a hard copy of the gog binary in the same trusted dir) via `exec` — no additional approval check. For dangerous writes, the wrapper blocks with an error message telling the LLM to use the full path `/usr/local/bin/gog` (which triggers exec-approval).

| Amber types | What happens | Approval? |
|------------|-------------------|-----------|
| `gog gmail messages search ...` | Wrapper matches safe pattern → `exec gog-real` | ✅ Auto-approved (both wrapper and gog-real are in trusted dir) |
| `gog gmail thread get ...` | Wrapper matches safe pattern → `exec gog-real` | ✅ Auto-approved |
| `gog gmail labels list` | Wrapper matches safe pattern → `exec gog-real` | ✅ Auto-approved |
| `gog gmail thread modify ...` | Wrapper matches safe pattern → `exec gog-real` | ✅ Auto-approved |
| `gog cal events ...` | Wrapper matches safe pattern → `exec gog-real` | ✅ Auto-approved |
| `gog gmail send ...` | Wrapper BLOCKS → error message | ❌ Blocked (must use `/usr/local/bin/gog`) |
| `gog cal create ...` | Wrapper BLOCKS → error message | ❌ Blocked |
| Any unknown command | Wrapper BLOCKS → error message | ❌ Blocked (safe default) |

### Install

```bash
# 1. Pull latest repo (wrapper is at scripts/gog)
cd ~/.openclaw/workspace && git pull origin main

# 2. Make it executable
chmod +x ~/.openclaw/workspace/scripts/gog

# 3. Create gog-real HARD COPY (CRITICAL — see "Why gog-real" below)
# NOTE: Must be a hard copy, NOT a symlink. OpenClaw resolves symlinks.
cp /usr/local/bin/gog /Users/amberives/.openclaw/workspace/scripts/gog-real

# 4. Add scripts directory to PATH BEFORE /usr/local/bin
echo 'export PATH="/Users/amberives/.openclaw/workspace/scripts:$PATH"' >> ~/.zshrc
source ~/.zshrc

# 5. Verify PATH resolution
which gog
# Should show: /Users/amberives/.openclaw/workspace/scripts/gog
# NOT: /usr/local/bin/gog

# 6. HARD KILL + restart gateway (critical — soft restart may not pick up PATH)
pkill -f openclaw-gateway && sleep 2 && openclaw gateway restart
```

**⚠️ Why gog-real:** OpenClaw monitors `exec()` calls. When the wrapper previously called `exec /usr/local/bin/gog`, OpenClaw saw a NEW binary execution outside the trusted dir and triggered approval — defeating the whole purpose. By copying the real binary INTO the trusted scripts dir as `gog-real`, the `exec` stays within trusted territory and auto-approves. The other wrapper scripts (`gog-email-read.sh`, `gog-email-tag.sh`, `gog-cal-read.sh`) also use `gog-real` for the same reason.

**⚠️ Why hard copy, NOT symlink:** OpenClaw resolves symlinks to their real path before checking `safeBinTrustedDirs`. We tried `ln -sf /usr/local/bin/gog .../gog-real` first — it failed because OpenClaw followed the symlink and saw `/usr/local/bin/gog` (not in trusted dir), triggering approval. A hard copy (`cp`) creates a real file in the trusted dir, which auto-approves. After `gog` binary updates (e.g., `brew upgrade`), re-copy:
```bash
rm /Users/amberives/.openclaw/workspace/scripts/gog-real
cp /usr/local/bin/gog /Users/amberives/.openclaw/workspace/scripts/gog-real
```

**⚠️ The hard kill (`pkill -f openclaw-gateway`) is essential.** A soft `openclaw gateway restart` may not spawn a new process that inherits the updated PATH. The gateway resolves binary paths using its own process PATH (set at startup). If the gateway was started before the PATH change, it won't see the wrapper.

### Test

```bash
# Read — should NOT trigger approval
gog gmail labels list

# Send — SHOULD trigger approval (LLM must use /usr/local/bin/gog for sends)
/usr/local/bin/gog gmail send --to "test@example.com" --subject "test" --body-html "<p>test</p>"
# (Cancel after verifying approval fires)
```

### How it works

The wrapper checks patterns in this order:
1. **Dangerous patterns first** (send, reply, delete, create) → BLOCKS with error message telling LLM to use `/usr/local/bin/gog`
2. **Safe patterns** (search, get, list, labels, thread modify, cal events) → `exec gog-real "$@"` (auto-approved because both wrapper and gog-real hard copy are in trusted dir)
3. **Anything else** → BLOCKS with error message (safe default)

This means even if Amber invents `gog` subcommands not in any docs (which she does — e.g., `gog gmail inbox`), unknown commands are blocked rather than silently failing or auto-approving.

**Why the wrapper blocks sends instead of passing through:** If sends passed through via `exec gog-real`, they'd auto-approve because gog-real is in the trusted dir — defeating the purpose. Blocking sends forces the LLM to call `/usr/local/bin/gog` directly for writes, which is NOT in safeBinTrustedDirs and triggers exec-approval.

**The gog-real chain:** `gog` (wrapper, trusted) → `exec gog-real` (hard copy in trusted dir) → auto-approved. But `/usr/local/bin/gog` called directly → NOT in trusted dir → triggers approval. This asymmetry is the security model.

### After reboots / gateway restarts

**⚠️ The PATH is fragile.** The gateway inherits PATH from the shell that starts it. If the gateway restarts automatically (crash, system reboot) from a context that doesn't read `~/.zshrc`, the scripts directory won't be in PATH and reads will start triggering approval again.

**If reads start prompting for approval again, run this from a terminal:**
```bash
export PATH="/Users/amberives/.openclaw/workspace/scripts:$PATH" && pkill -f openclaw-gateway && sleep 2 && openclaw gateway restart
```

This ensures the gateway process inherits the correct PATH with the scripts directory first.

**⚠️ Intel vs Apple Silicon:** Homebrew installs to `/usr/local` on Intel Macs and `/opt/homebrew` on Apple Silicon. Amber's MacBook Air is Intel, so `/opt/homebrew/bin` does NOT exist. Don't attempt to symlink anything there.

### Updating

The wrapper lives in the git repo at `scripts/gog`. After `git pull`, it's updated in place — no re-copy needed.

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

Add trusted directories so basic shell tools and wrapper scripts don't trigger approval:
```bash
openclaw config set tools.exec.safeBinTrustedDirs '["/bin", "/usr/bin", "/opt/homebrew/bin", "/Users/amberives/.openclaw/workspace/scripts"]'
```

**⚠️ Why this directory matters:**
- **`/Users/amberives/.openclaw/workspace/scripts`** — trusts the wrapper scripts (`gog-email-read.sh`, `gog-cal-read.sh`, `gog-email-tag.sh`). The gog-guard plugin rewrites read/tag commands to use these scripts, so they must be trusted for auto-approval to work.

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
gog gmail labels list
```
(Plugin rewrites this to the wrapper script automatically.)

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
gog gmail messages search 'is:unread -label:Handled -from:daver@mindfireinc.com' --max 25
```
(The gog-guard plugin will rewrite this to use the wrapper script automatically.)

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
- [ ] `which gog` shows `/Users/amberives/.openclaw/workspace/scripts/gog` (PATH wrapper active)
- [ ] `gog gmail labels list` does NOT trigger approval (wrapper routes to gog-email-read.sh)
- [ ] `gog gmail threads modify` does NOT trigger approval (wrapper routes to gog-email-tag.sh)
- [ ] `gog gmail send` DOES trigger approval (wrapper passes to /usr/local/bin/gog)
- [ ] Approval prompts arrive in Dave's PRIVATE Telegram, not Amber's channel
- [ ] grep/cat/ls don't trigger approval
- [ ] `cat ~/.openclaw/exec-approvals.json` shows no raw `gog` entry in **`agents.main.allowlist`**
- [ ] Basename entries (`gog-email-read.sh`, `gog-cal-read.sh`) are in **`agents.main.allowlist`** (not just `agents.*`)
- [ ] `askFallback` is set to `"deny"` in exec-approvals.json
- [ ] Email backlog is being processed

### Troubleshooting: Reads still trigger approval

If `gog gmail labels list` triggers approval after setup:

1. **Check which gog resolves to.** Run `which gog` — should show `/Users/amberives/.openclaw/workspace/scripts/gog`. If it shows `/usr/local/bin/gog`, the scripts directory isn't in PATH. Fix:
   ```bash
   export PATH="/Users/amberives/.openclaw/workspace/scripts:$PATH"
   ```

2. **Hard kill the gateway.** A soft `openclaw gateway restart` may not pick up PATH changes. Always use:
   ```bash
   pkill -f openclaw-gateway && sleep 2 && openclaw gateway restart
   ```

3. **Check `safeBinTrustedDirs`.** Run `openclaw config get tools.exec.safeBinTrustedDirs` — the scripts directory (`/Users/amberives/.openclaw/workspace/scripts`) must be listed.

4. **Check the approval prompt path.** When approval fires, look at the binary path shown. If it says `/usr/local/bin/gog`, the gateway is still resolving to the real binary (PATH not inherited). If it says `/Users/amberives/.openclaw/workspace/scripts/gog`, the wrapper is being called but isn't in a trusted dir.

5. **After reboots:** The gateway may restart without the correct PATH. Run from a terminal:
   ```bash
   export PATH="/Users/amberives/.openclaw/workspace/scripts:$PATH" && pkill -f openclaw-gateway && sleep 2 && openclaw gateway restart
   ```

### Troubleshooting: gog commands timing out

If gog commands hang or time out:

1. **Check gog auth.** Run `gog auth status` — may need to re-authenticate: `gog auth login`
2. **Check network.** Run `curl -s https://gmail.googleapis.com` — should get a response
3. **Try with explicit timeout.** `timeout 30 gog gmail labels list` — to distinguish between auth hang vs network issue

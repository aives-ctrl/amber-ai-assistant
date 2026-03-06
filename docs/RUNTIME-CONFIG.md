# Runtime Configuration

These settings need to be verified/updated on Amber's machine in `~/.openclaw/openclaw.json` (or via `openclaw config set`). They are NOT managed by the Git repo because they contain machine-specific paths and IDs.

---

## 1. Memory Flush (Prevents context loss on session compaction)

```json5
// In agents.defaults or agents.<agentId>:
compaction: {
  memoryFlush: {
    enabled: true,
    softThresholdTokens: 4000
  }
}
```

When a session approaches context limits, this triggers a silent turn reminding Amber to persist important context to daily notes before compaction drops it.

## 2. Memory Search (Hybrid search for better recall)

```json5
memorySearch: {
  enabled: true,
  query: {
    hybrid: {
      enabled: true,
      vectorWeight: 0.7,
      textWeight: 0.3,
      temporalDecay: {
        enabled: true,
        halfLifeDays: 30
      }
    }
  }
}
```

Combines semantic (vector) search with keyword (BM25) search. Temporal decay ensures recent memories rank higher.

## 3. Exec-Approvals (Read-Only Operations) -- CONFIGURED

The goal: email/calendar READS flow freely, SENDS require Dave's Telegram approval.

### Working Configuration (as of 2026-03-04)

**`openclaw.json`** sets the exec policy (allowlist mode + on-miss behavior):
```json
{
  "tools": {
    "exec": {
      "host": "gateway",
      "security": "allowlist",
      "ask": "on-miss",
      "autoAllowSkills": false,
      "askFallback": "deny"
    }
  }
}
```

**⚠️ The allowlist itself is NOT in `openclaw.json`.** It lives in `~/.openclaw/exec-approvals.json` and is managed via CLI:
```bash
openclaw approvals allowlist add "/Users/amberives/.openclaw/workspace/scripts/gog-*"
cat ~/.openclaw/exec-approvals.json  # verify entries
openclaw approvals allowlist remove <path>  # if needed
```

**Do NOT put `"allowlist": [...]` in `openclaw.json`** — it's an unrecognized key and will crash the gateway.

**Allowlisted paths:**
- `/Users/amberives/.openclaw/workspace/scripts/gog-*` (glob covers all gog wrapper scripts)

**⚠️ The ONLY valid path for wrapper scripts is `/Users/amberives/.openclaw/workspace/scripts/`.** Do NOT use `/usr/local/bin/` — the scripts are not symlinked there.

**Also allowlist basic shell tools** (prevents grep, cat, ls from triggering approval):
```bash
openclaw approvals allowlist add "/usr/bin/grep"
openclaw approvals allowlist add "/usr/bin/cat"
openclaw approvals allowlist add "/usr/bin/ls"
openclaw approvals allowlist add "/opt/homebrew/bin/grep"
```

**CRITICAL: Amber must use FULL PATHS when calling wrapper scripts.**
The allowlist matches on resolved binary paths. Calling by basename may not resolve correctly. Always use the full path:
```bash
/Users/amberives/.openclaw/workspace/scripts/gog-email-read.sh gmail labels list     # ✅ no approval
/Users/amberives/.openclaw/workspace/scripts/gog-cal-read.sh cal events ...           # ✅ no approval
gog gmail send ...                                                                     # 🔒 triggers approval
```

See `skills/email-read/SKILL.md` and `skills/calendar-read/SKILL.md` for the canonical command patterns.

**How it works:**
- Wrapper scripts are allowlisted -- email/calendar reads flow without approval
- Raw `gog` (`/usr/local/bin/gog`) is NOT on the allowlist -- sends trigger approval via Telegram
- `on-miss` = "ask" -- any unlisted command prompts Dave for approval rather than being blocked

**⚠️ DANGER: "Always Allow" Breaks the Security Gate**

The allowlist matches on RESOLVED BINARY PATHS, not subcommands. The `gog` binary is a single executable with multiple subcommands (`gmail search`, `gmail send`, `calendar events`, etc.). If the `gog` binary path gets added to the allowlist (via "Always Allow" button tap or `allow-always` command), ALL gog subcommands bypass approval, including `gog gmail send`.

**Rule: Only use "Allow Once" for `gog` commands. NEVER "Always Allow."**

If `gog` accidentally gets always-allowed, fix it:
```bash
cat ~/.openclaw/exec-approvals.json        # find the gog entry
openclaw approvals allowlist remove "<path-to-gog>"  # remove it
openclaw gateway restart                    # reload config
```

**Additional safety settings (REQUIRED):**
```json
{
  "tools": {
    "exec": {
      "autoAllowSkills": false,
      "askFallback": "deny"
    }
  }
}
```
- `autoAllowSkills: false` -- Prevents `gog` from being implicitly allowlisted as a registered OpenClaw skill
- `askFallback: "deny"` -- If approval UI is unavailable (e.g., during gateway restart), commands are DENIED, not auto-approved

Set via CLI:
```bash
openclaw config set tools.exec.autoAllowSkills false
```

**⚠️ `askFallback` cannot be set via CLI** (there is no `openclaw approvals defaults` subcommand). It must be set by editing `~/.openclaw/exec-approvals.json` directly. Add `"askFallback": "deny"` to the `"defaults"` section of that file.

### Approval Timeout

The default exec-approval timeout is 120s. The timeout is NOT a global config setting -- it's passed per-command by Amber when she invokes exec calls. AGENTS.md and TOOLS.md instruct her to use `timeout: 3600` in her exec calls so Dave has 60 min to respond on his phone.

**Do NOT add `"timeout"` to `openclaw.json`** -- OpenClaw will reject it as an unrecognized key.

### If allowlist needs updating

1. `cat ~/.openclaw/exec-approvals.json` — see current entries (note: `openclaw approvals allowlist list` may not exist in all versions)
2. `openclaw approvals allowlist add <full-path>` — add new entry
3. `openclaw approvals allowlist remove <full-path>` — remove entry
4. Test: `/Users/amberives/.openclaw/workspace/scripts/gog-email-read.sh gmail labels list` — should work without approval
5. Test: `gog gmail send ...` — should still trigger approval

## 4. Session Pruning & Context Cost Control

Long sessions are the #1 cost driver. A 267-message session cost $59.30 because each message carried 100-130k tokens of cached context. These settings prevent that.

### A. Cache-TTL Pruning (trims stale tool output)

```json5
agents: {
  defaults: {
    contextPruning: {
      mode: "cache-ttl",
      ttl: "5m"
    }
  }
}
```

Or via CLI:
```bash
openclaw config set agents.defaults.contextPruning.mode cache-ttl
openclaw config set agents.defaults.contextPruning.ttl 5m
```

**⚠️ The config path is `agents.defaults.contextPruning`, NOT `session.pruning`.** The `session.pruning` keys do not exist and will fail silently.

This trims old tool results from in-memory context before each LLM call. Does NOT modify on-disk session history. Biggest single cost saver.

### B. Context Token Limit (prevents runaway growth)

```json5
agents: {
  defaults: {
    contextTokens: 50000
  }
}
```

Or via CLI: `openclaw config set agents.defaults.contextTokens 50000`

**⚠️ The config path is `agents.defaults.contextTokens`, NOT `session.contextTokens`.**

Without this, the agent uses the full model context window (~200k tokens). Capping at 50k forces automatic summarization when context grows too large, keeping per-message costs low.

### C. Compact Long Sessions (Amber's responsibility)

Amber should run `/compact` proactively every ~15 turns during long sessions. This is the "Pulse Strategy":
1. Let context build for 10-15 turns
2. Run `/compact` to lock in decisions and drop noise
3. Repeat

This is documented in AGENTS.md as a mandatory practice for multi-hour sessions.

### D. Heartbeat Cache Warming

If Anthropic's cache TTL is 5min (short), set heartbeat interval slightly under to prevent expensive full cache rewrites. Current heartbeat is every 30min (section 5). If using short cache retention, consider reducing to every 4-5 min during active hours — but weigh against the cost of each heartbeat call.

For API key profiles, the default cache retention is "short" (5min). For OAuth/setup-token profiles, it may be longer. Check with: `openclaw config get model.cacheRetention`

### E. Workspace File Audit

Every config file (AGENTS.md, SOUL.md, TOOLS.md, etc.) is loaded into the system prompt on every turn. Every line costs tokens. Periodically audit and trim unused or redundant instructions. Target: keep total workspace config under 10k tokens.

---

## 5. Session Identity Links (Cross-channel continuity)

```json5
session: {
  identityLinks: {
    dave: [
      "telegram:<DAVE_TELEGRAM_ID>",
      "ringcentral-sms:<DAVE_RC_NUMBER>",
      "ringcentral-team:<DAVE_RC_TEAM_ID>"
    ]
  }
}
```

Replace the placeholder values with Dave's actual IDs. This maps all of Dave's channel identities to a single shared session so context persists across Telegram, SMS, and RC Team Chat.

To find Dave's Telegram ID: run `openclaw sessions` (no subcommand) for his existing Telegram session key.
To find Dave's RC identifiers: check the RC plugin config or session keys.

## 6. Heartbeat Configuration

```json5
agents: {
  defaults: {
    heartbeat: {
      every: "30m",
      activeHours: {
        start: "06:20",
        end: "22:00",
        timezone: "America/Los_Angeles"
      }
    }
  }
}
```

## 7. Heartbeat Model (Use Sonnet to save costs)

```json5
agents: {
  defaults: {
    heartbeat: {
      model: "anthropic/claude-sonnet-4-20250514"
    }
  }
}
```

## 8. Prompt Caching

Cache retention is configured per-profile under `agents.defaults`:

```json5
agents: {
  defaults: {
    cacheRetention: "long"   // or "short" — depends on profile type
  }
}
```

Check current setting: `openclaw config get agents.defaults | grep cacheRetention`

**⚠️ `model.caching` does not exist.** The old `openclaw config set model.caching true` command is wrong. Cache retention is already configured by default (API key profiles get "short", OAuth/setup-token profiles get "long"). No action needed unless you want to change the retention period.

## 9. Approval Channel Separation (PREVENTS SELF-APPROVAL)

**Problem:** Amber operates in the same Telegram chat where `/approve` commands are processed. She can self-approve her own commands by typing `/approve <UUID> allow-once` in the same chat.

**Fix:** Route exec approvals to Dave's PERSONAL Telegram DM with the bot, not the group/channel Amber uses.

```json5
approvals: {
  exec: {
    enabled: true,
    targets: [
      { channel: "telegram", to: "8703088279" }
    ]
  }
}
```

Dave's Telegram user ID is `8703088279`. To verify: run `openclaw sessions` (no subcommand) or DM `@userinfobot` on Telegram.

This way:
- Amber converses in her regular Telegram channel
- Approval prompts go to Dave's PRIVATE DM with the bot
- Amber has no access to Dave's private chat, so she cannot self-approve
- The telegram-approval-buttons plugin still works (buttons show in Dave's private chat)

**CRITICAL:** This is the only reliable way to prevent self-approval. Config rules telling Amber "don't self-approve" are insufficient because the model will do it under pressure (we've observed this).

### Troubleshooting: Approvals Appearing in Both Channels

If approval prompts show up in BOTH Dave's private DM AND Amber's session channel (even though `mode: "targets"` is set correctly), the `telegram-approval-buttons` plugin may be independently injecting approval UI into the session channel regardless of the core routing config.

**Debug steps:**
```bash
openclaw plugins config telegram-approval-buttons   # check plugin-level routing config
openclaw plugins list                                # verify plugin is loaded
```

If the plugin has its own `target` or `chatId` setting, update it to match Dave's personal chat ID (`8703088279`). If it doesn't have a separate routing config, you may need to disable the plugin and rely on core approval routing:
```bash
openclaw plugins disable telegram-approval-buttons
openclaw gateway restart
```

The core approval routing (`mode: "targets"`) should work without the plugin — the plugin just adds inline buttons for convenience. Test whether disabling it fixes the dual-channel issue.

## 10. Safe Bins Configuration (Shell Tool & Wrapper Script Approvals)

**Problem:** Basic shell commands like `grep`, `cat`, `ls` trigger exec-approval even though they're harmless. Additionally, the exec-approval allowlist matching can fail on wrapper scripts even when correct paths are in the allowlist (the matcher appears to use the command-as-called before resolving to full path, so relative calls fail).

**Fix:** Use `safeBinTrustedDirs` to trust entire directories, bypassing allowlist path matching:

```json5
tools: {
  exec: {
    safeBinTrustedDirs: ["/bin", "/usr/bin", "/opt/homebrew/bin", "/Users/amberives/.openclaw/workspace/scripts"]
  }
}
```

Or via CLI:
```bash
openclaw config set tools.exec.safeBinTrustedDirs '["/bin", "/usr/bin", "/opt/homebrew/bin", "/Users/amberives/.openclaw/workspace/scripts"]'
```

**⚠️ Including the scripts directory is critical.** The wrapper scripts (`gog-email-read.sh`, `gog-cal-read.sh`) enforce their own read-only allowlists internally, so trusting the directory is safe — write operations still require going through raw `gog` which is NOT in a trusted directory.

Also explicitly allowlist commonly used tools as backup:
```bash
openclaw approvals allowlist add "/usr/bin/grep"
openclaw approvals allowlist add "/usr/bin/cat"
openclaw approvals allowlist add "/usr/bin/ls"
openclaw approvals allowlist add "/opt/homebrew/bin/grep"
openclaw approvals allowlist add "/usr/bin/python3"
```

## 11. Gmail PubSub Integration (Push-Based Email)

**Goal:** Instead of Amber polling every 30 minutes, Gmail pushes new emails to OpenClaw in real time.

**Setup:**
```bash
gog gmail watch serve \
  --topic projects/<GCP_PROJECT>/topics/gog-gmail-watch \
  --account aives@mindfiremail.info \
  --label INBOX \
  --include-body --max-bytes 4096 \
  --hook-url http://127.0.0.1:18789/hook/gmail \
  --hook-token "$OPENCLAW_HOOK_TOKEN"
```

**Config in openclaw.json:**
```json5
hooks: {
  gmail: {
    model: "anthropic/claude-sonnet-4-20250514",
    sessionKey: "email-{{messageId}}",
    channel: "last"
  }
}
```

**Benefits:**
- Emails arrive in real time (not 30-minute polling)
- Email content is pre-fetched (no search/get exec calls needed)
- Heartbeat becomes backup, not primary mechanism
- Eliminates 80% of exec calls that currently cause approval friction

**Prerequisites:**
- ~~Google Calendar API must be enabled~~ ✅ Enabled (2026-03-04)
- GCP Pub/Sub topic must be created
- `OPENCLAW_HOOK_TOKEN` must be set in environment

## 12. Skills and Workflows

**Skills** are defined in `~/.openclaw/workspace/skills/` and provide Amber with canonical patterns for common operations. They replace ad-hoc exec commands with documented, repeatable workflows.

Current skills (in git repo under `skills/`):
- `email-read/` - Read-only email operations (search, get, thread, labels)
- `email-send/` - Send emails with mandatory draft-first approval
- `calendar-read/` - Read-only calendar operations
- `calendar-create/` - Create events with approval
- `startup/` - Session initialization (load context before responding)

**Lobster Workflows** are defined in `workflows/` and provide multi-step pipelines with single approval gates.

Current workflows:
- `email-triage.lobster` - Full inbox processing pipeline (search -> read -> categorize -> draft -> send)

After `git pull`, these are available at `~/.openclaw/workspace/skills/` and `~/.openclaw/workspace/workflows/`.

## 13. Known Issue: `memory_search` Triggering Exec Approval

`memory_search` is a built-in OpenClaw tool (registered in the `memory-core` extension). It is NOT an exec call and should NOT trigger exec-approval. If it does, this is a **tool policy** issue, not an exec-approval allowlist issue.

**Debug steps:**
```bash
openclaw config get tools          # check if memory_search or group:memory is in a deny/ask list
openclaw config get agents.defaults.tools   # check agent-level tool policies
```

If a tool policy is blocking it, fix by ensuring `memory_search` (or `group:memory`) is in the `allow` list:
```bash
openclaw config set agents.defaults.tools.allow '["group:memory", "group:exec"]'
```

If there's no explicit policy blocking it, this may be a bug in the OpenClaw version — check with `openclaw --version` and look for known issues.

---

## Verification Checklist

After applying these settings, verify by running:

1. `openclaw config get compaction.memoryFlush.enabled` -- should be `true`
2. `openclaw config get memorySearch.enabled` -- should be `true`
3. `openclaw config get agents.defaults | grep cacheRetention` -- should show "long" or "short"
4. `openclaw sessions` -- check that Dave's sessions share an identity key
5. Have Amber check email with full-path wrapper -- should NOT trigger approval:
   `/Users/amberives/.openclaw/workspace/scripts/gog-email-read.sh gmail labels list`
6. Have Amber try `gog gmail send` -- SHOULD trigger approval
7. If step 5 triggers approval: check `cat ~/.openclaw/exec-approvals.json` and fix paths, or verify scripts dir is in `safeBinTrustedDirs`
8. `grep -i "brenda" memory/*.md` -- should NOT trigger approval (grep is in trusted dir)

### Exec-Approval Safety Checks (run periodically)

9. `cat ~/.openclaw/exec-approvals.json` -- raw `gog` binary should NOT appear in allowlist. Only wrapper scripts + shell tools.
10. Approval prompts should arrive in Dave's PRIVATE Telegram chat, not the agent's channel
11. `cat ~/.openclaw/exec-approvals.json | grep -i autoAllowSkills` -- should be `false`
12. `cat ~/.openclaw/exec-approvals.json | grep -i askFallback` -- should be `"deny"`
13. If `gog gmail send` does NOT trigger approval, the gate is broken. Run the fix commands in Section 3.

### Skills Verification

14. `ls ~/.openclaw/workspace/skills/` -- should show: email-read, email-send, calendar-read, calendar-create, startup
15. `ls ~/.openclaw/workspace/workflows/` -- should show: email-triage.lobster
16. After `/new`, Amber should run `startup` skill before responding (check daily notes for startup log)

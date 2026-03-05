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

In `~/.openclaw/openclaw.json` under `tools.exec`:
```json
{
  "tools": {
    "exec": {
      "host": "gateway",
      "security": "allowlist",
      "ask": "on-miss",
      "allowlist": [
        "<RESOLVED_PATH_TO_gog-email-read.sh>",
        "<RESOLVED_PATH_TO_gog-cal-read.sh>"
      ]
    }
  }
}
```

**CRITICAL: Allowlist paths must match the RESOLVED binary path.**
The allowlist matches the exact path the shell resolves when running the command. Run `which gog-email-read.sh` and `which gog-cal-read.sh` to get the actual paths, and use THOSE in the allowlist. If scripts are symlinked to `/usr/local/bin/`, use the `/usr/local/bin/` paths. If they live in `~/.openclaw/workspace/scripts/`, use those. A mismatch = every read triggers approval.

**How it works:**
- Wrapper scripts are allowlisted -- email/calendar reads flow without approval
- Raw `gog` (`/usr/local/bin/gog`) is NOT on the allowlist -- sends trigger approval via Telegram
- `on-miss` = "ask" -- any unlisted command prompts Dave for approval rather than being blocked

### Approval Timeout

The default exec-approval timeout is 120s. The timeout is NOT a global config setting -- it's passed per-command by Amber when she invokes exec calls. AGENTS.md and TOOLS.md instruct her to use `timeout: 3600` in her exec calls so Dave has 60 min to respond on his phone.

**Do NOT add `"timeout"` to `openclaw.json`** -- OpenClaw will reject it as an unrecognized key.

### If allowlist needs updating

1. Find resolved paths: `realpath ~/.openclaw/workspace/scripts/gog-email-read.sh`
2. Edit `~/.openclaw/openclaw.json` and update the `allowlist` array
3. Test: `gog-email-read.sh gmail labels list` should work without approval
4. Test: `gog gmail send ...` should still trigger approval

## 4. Session Pruning & Context Cost Control

Long sessions are the #1 cost driver. A 267-message session cost $59.30 because each message carried 100-130k tokens of cached context. These settings prevent that.

### A. Cache-TTL Pruning (trims stale tool output)

```json5
session: {
  pruning: {
    mode: "cache-ttl",
    ttl: "5m"
  }
}
```

Or via CLI: `openclaw config set session.pruning.mode cache-ttl && openclaw config set session.pruning.ttl 5m`

This trims old tool results from in-memory context before each LLM call. Does NOT modify on-disk session history. Biggest single cost saver.

### B. Context Token Limit (prevents runaway growth)

```json5
session: {
  contextTokens: 50000
}
```

Or via CLI: `openclaw config set session.contextTokens 50000`

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

To find Dave's Telegram ID: check `openclaw sessions list` for his existing Telegram session key.
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

```json5
model: {
  caching: true
}
```

Or via CLI: `openclaw config set model.caching true`

This can cut API bills by 50-70% by caching the system prompt across calls.

---

## Verification Checklist

After applying these settings, verify by running:

1. `openclaw config get compaction.memoryFlush.enabled` -- should be `true`
2. `openclaw config get memorySearch.enabled` -- should be `true`
3. `openclaw config get model.caching` -- should be `true`
4. `openclaw sessions list` -- check that Dave's sessions share an identity key
5. Have Amber check email with `gog-email-read.sh gmail labels list` -- should NOT trigger approval
6. Have Amber try `gog gmail send` -- SHOULD trigger approval
7. If step 5 triggers approval, run the troubleshooting commands in section 3 above and report output to Dave

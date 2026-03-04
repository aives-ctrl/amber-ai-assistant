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

## 3. Exec-Approvals (Read-Only Operations)

The goal: email/calendar READS flow freely, SENDS require Dave's Telegram approval.

### Option A: Allowlist the wrapper scripts (preferred)

In `~/.openclaw/exec-approvals.json` (or `openclaw config set`):

1. Find the RESOLVED paths of the wrapper scripts:
```bash
realpath ~/.openclaw/workspace/scripts/gog-email-read.sh
realpath ~/.openclaw/workspace/scripts/gog-cal-read.sh
```

2. Add those exact paths to the allowlist:
```json5
agents: {
  main: {
    allowlist: [
      // ... existing entries ...
      "<RESOLVED_PATH>/gog-email-read.sh",
      "<RESOLVED_PATH>/gog-cal-read.sh"
    ]
  }
}
```

3. Verify that raw `gog` is NOT on the allowlist.

### Option B: If wrappers still trigger on-miss

If the wrapper scripts trigger `on-miss` even after adding their resolved paths, the likely cause is that OpenClaw intercepts the `exec gog` call INSIDE the script (the nested execution). In that case:

**Approach B1 -- Allowlist gog with on-miss=ask (not deny):**
```json5
agents: {
  main: {
    allowlist: [
      // ... existing entries ...
      "<RESOLVED_PATH>/gog-email-read.sh",
      "<RESOLVED_PATH>/gog-cal-read.sh"
    ],
    onMiss: "ask"   // Changed from "deny" to "ask"
  }
}
```
This means the first time Amber runs a wrapper, Dave approves once, and after that it flows. Not ideal but functional.

**Approach B2 -- Allowlist gog itself with argument patterns (if supported):**
Check if OpenClaw supports argument-level allowlisting:
```json5
allowlist: [
  { "path": "/usr/local/bin/gog", "args": ["gmail", "messages", "search", "*"] },
  { "path": "/usr/local/bin/gog", "args": ["gmail", "messages", "get", "*"] },
  { "path": "/usr/local/bin/gog", "args": ["gmail", "thread", "get", "*"] },
  { "path": "/usr/local/bin/gog", "args": ["cal", "events", "*"] }
]
```
Run `openclaw help exec-approvals` to check if argument patterns are supported.

**Approach B3 -- Use allow-always for wrappers only:**
When the approval prompt fires for a wrapper script call, approve with `allow-always` for that specific script path. Raw `gog` calls should still use `allow-once`.

### Troubleshooting

If wrappers trigger `on-miss`, run these diagnostic commands:
```bash
# 1. Check what path OpenClaw resolves for the scripts
which gog-email-read.sh
realpath $(which gog-email-read.sh 2>/dev/null || echo ~/.openclaw/workspace/scripts/gog-email-read.sh)

# 2. Check what's currently on the allowlist
openclaw config get agents.main.allowlist

# 3. Check if gog itself is on the allowlist (it should NOT be)
which gog
openclaw config get agents.main.allowlist | grep gog

# 4. Check the exec-approval on-miss policy
openclaw config get agents.main.onMiss

# 5. Test with verbose logging
OPENCLAW_LOG=debug gog-email-read.sh gmail labels list
```

Report the output back to Dave so Claude Code can diagnose further.

## 4. Session Identity Links (Cross-channel continuity)

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

## 5. Heartbeat Configuration

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

## 6. Heartbeat Model (Use Sonnet to save costs)

```json5
agents: {
  defaults: {
    heartbeat: {
      model: "anthropic/claude-sonnet-4-20250514"
    }
  }
}
```

## 7. Prompt Caching

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

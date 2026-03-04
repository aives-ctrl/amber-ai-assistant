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
        "/Users/amberives/.openclaw/workspace/scripts/gog-email-read.sh",
        "/Users/amberives/.openclaw/workspace/scripts/gog-cal-read.sh"
      ]
    }
  }
}
```

**How it works:**
- Wrapper scripts are allowlisted -- email/calendar reads flow without approval
- Raw `gog` (`/usr/local/bin/gog`) is NOT on the allowlist -- sends trigger approval via Telegram
- `on-miss` = "ask" -- any unlisted command prompts Dave for approval rather than being blocked

### If allowlist needs updating

1. Find resolved paths: `realpath ~/.openclaw/workspace/scripts/gog-email-read.sh`
2. Edit `~/.openclaw/openclaw.json` and update the `allowlist` array
3. Test: `gog-email-read.sh gmail labels list` should work without approval
4. Test: `gog gmail send ...` should still trigger approval

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

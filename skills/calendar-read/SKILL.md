# calendar-read

Read-only calendar operations. List events, check availability, get event details.

## When to Use
- Checking Dave's upcoming schedule
- Looking for conflicts before scheduling
- Getting details on a specific event
- Calendar reminders (heartbeat)

## Commands

All commands use the read-only wrapper script. This is allowlisted and does NOT require exec approval.

```bash
# List events for a time range
/Users/amberives/.openclaw/workspace/scripts/gog-cal-read.sh cal events daver@mindfireinc.com --from "2026-03-04T00:00:00" --to "2026-03-04T23:59:59"

# Next 4 hours (for heartbeat)
/Users/amberives/.openclaw/workspace/scripts/gog-cal-read.sh cal events daver@mindfireinc.com --from now --to +4h

# Get specific event details
/Users/amberives/.openclaw/workspace/scripts/gog-cal-read.sh cal get daver@mindfireinc.com <eventId>

# List all calendars
/Users/amberives/.openclaw/workspace/scripts/gog-cal-read.sh cal list
```

## Rules

- ALWAYS use the FULL PATH: `/Users/amberives/.openclaw/workspace/scripts/gog-cal-read.sh`
- NEVER use basename `gog-cal-read.sh` (allowlist won't match)
- NEVER use raw `gog cal events` for reads (triggers approval)
- Dave's calendar ID is always: `daver@mindfireinc.com`
- ALWAYS verify day-of-week with `session_status` before stating dates
- Run commands ONE AT A TIME, sequentially.

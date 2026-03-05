# calendar-read

Read-only calendar operations. List events, check availability, get event details.

## When to Use
- Checking Dave's upcoming schedule
- Looking for conflicts before scheduling
- Getting details on a specific event
- Calendar reminders (heartbeat)

## Commands

All read commands use the **allowlisted wrapper script** `gog-cal-read.sh`. This script is pre-approved — no exec approval needed. **Always use the full path shown below.**

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

- **ALWAYS use the full wrapper script path** for read commands: `/Users/amberives/.openclaw/workspace/scripts/gog-cal-read.sh`
- **NEVER use bare `gog`** for reads — it will trigger exec-approval and slow you down
- Dave's calendar ID is always: `daver@mindfireinc.com`
- ALWAYS verify day-of-week with `session_status` before stating dates
- Run commands ONE AT A TIME, sequentially.

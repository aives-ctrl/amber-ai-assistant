# calendar-read

Read-only calendar operations. List events, check availability, get event details.

## When to Use
- Checking Dave's upcoming schedule
- Looking for conflicts before scheduling
- Getting details on a specific event
- Calendar reminders (heartbeat)

## Commands

All read commands use `gog` directly. The **gog-guard plugin** automatically rewrites these to use the allowlisted wrapper scripts — no exec approval needed.

```bash
# List events for a time range
gog cal events daver@mindfireinc.com --from "2026-03-04T00:00:00" --to "2026-03-04T23:59:59"

# Next 4 hours (for heartbeat)
gog cal events daver@mindfireinc.com --from now --to +4h

# Get specific event details
gog cal get daver@mindfireinc.com <eventId>

# List all calendars
gog cal list
```

## Rules

- Use `gog` for all read commands — the gog-guard plugin routes them to safe wrapper scripts automatically
- Dave's calendar ID is always: `daver@mindfireinc.com`
- ALWAYS verify day-of-week with `session_status` before stating dates
- Run commands ONE AT A TIME, sequentially.

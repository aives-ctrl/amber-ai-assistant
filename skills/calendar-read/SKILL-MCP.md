# calendar-read (MCP Version)

Read-only calendar operations via MCP wrapper. List events, check availability, get event details.

`mcp-read.sh` is on the exec allowlist — no approval needed.

## When to Use
- Checking Dave's upcoming schedule
- Looking for conflicts before scheduling
- Getting details on a specific event
- Calendar reminders (heartbeat)

## Command Reference

```bash
# List events for a time range
mcp-read.sh get_events --calendar_id "daver@mindfireinc.com" --time_min "2026-03-04T00:00:00" --time_max "2026-03-04T23:59:59"

# Next 4 hours (for heartbeat)
mcp-read.sh get_events --calendar_id "daver@mindfireinc.com" --time_min "<now-ISO-timestamp>" --time_max "<4-hours-from-now-ISO-timestamp>"

# Get a specific event by ID
mcp-read.sh get_events --calendar_id "daver@mindfireinc.com" --event_id "<eventId>"

# List all calendars
mcp-read.sh list_calendars
```

Note: `user_google_email` is automatically set to `aives@mindfiremail.info` by the script — you never need to pass it.

## Rules

- `mcp-read.sh` is auto-approved — no Telegram prompt needed
- Dave's calendar ID is always: `daver@mindfireinc.com`
- ALWAYS verify day-of-week with `session_status` before stating dates
- Run commands ONE AT A TIME, sequentially

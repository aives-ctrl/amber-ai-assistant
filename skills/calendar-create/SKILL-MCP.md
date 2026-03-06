# calendar-create (MCP Version)

Create or update calendar events via MCP wrapper. ALWAYS requires Dave's approval.

`mcp-write.sh create_event` and `mcp-write.sh modify_event` are NOT on the exec allowlist — every call triggers approval via Telegram.
`delete_event` is blocked in `mcp-write.sh` — Dave must delete events manually.

## When to Use
- Creating new calendar events
- Updating existing events
- Any write operation on the calendar

## Process (MANDATORY)

1. **Check for conflicts first** using calendar-read skill (`mcp-read.sh get_events`)
2. **Verify the day-of-week** with `session_status` before proposing a date
3. **Propose the event to Dave on Telegram:**
   - Date, time, duration
   - Attendees
   - Any conflicts detected
   - "Create it? Or adjust?"
4. **Wait for Dave's approval**
5. **Create the event** using mcp-write.sh (exec-approval will prompt via Telegram)
6. Log to daily notes

## Command Reference

```bash
# Create event
mcp-write.sh create_event \
  --calendar_id "daver@mindfireinc.com" \
  --summary "Meeting Name" \
  --start "2026-03-05T10:00:00" \
  --end "2026-03-05T11:00:00" \
  --description "Meeting description"

# Create event with attendees (use --json-body for arrays)
mcp-write.sh create_event --json-body '{"calendar_id":"daver@mindfireinc.com","summary":"Meeting Name","start":"2026-03-05T10:00:00","end":"2026-03-05T11:00:00","description":"Meeting description","attendees":["person@example.com","other@example.com"]}'

# Modify existing event
mcp-write.sh modify_event \
  --calendar_id "daver@mindfireinc.com" \
  --event_id "<eventId>" \
  --summary "Updated Meeting Name" \
  --start "2026-03-05T10:30:00" \
  --end "2026-03-05T11:30:00"
```

## Rules

- NEVER create events without Dave's approval
- ALWAYS check calendar for conflicts before proposing
- ALWAYS verify date matches expected day-of-week
- NEVER commit Dave to meetings without his OK
- One calendar command at a time. Never batch.
- delete_event is BLOCKED in mcp-write.sh — Dave must delete manually in Google Calendar

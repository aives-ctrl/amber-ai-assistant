# calendar-create (MCP Version)

Create or update calendar events via MCP wrapper. ALWAYS requires Dave's approval.

The MCP tool is `manage_event` with an `action` parameter: `create`, `update`, or `delete`.

`mcp-write.sh manage_event` is NOT on the exec allowlist — every call triggers approval via Telegram.
`manage_event` with `action=delete` is BLOCKED in `mcp-write.sh` — Dave must delete events manually.

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

**IMPORTANT: All timestamps MUST include timezone offset (e.g., `-08:00` for Pacific).** Without it, the Google Calendar API rejects the request.

```bash
# Create event
mcp-write.sh manage_event \
  --action "create" \
  --calendar_id "daver@mindfireinc.com" \
  --summary "Meeting Name" \
  --start_time "2026-03-05T10:00:00-08:00" \
  --end_time "2026-03-05T11:00:00-08:00" \
  --description "Meeting description"

# Create event with attendees (use --json-body for arrays)
mcp-write.sh manage_event --json-body '{"action":"create","calendar_id":"daver@mindfireinc.com","summary":"Meeting Name","start_time":"2026-03-05T10:00:00-08:00","end_time":"2026-03-05T11:00:00-08:00","description":"Meeting description","attendees":["person@example.com","other@example.com"]}'

# Update existing event
mcp-write.sh manage_event \
  --action "update" \
  --calendar_id "daver@mindfireinc.com" \
  --event_id "<eventId>" \
  --summary "Updated Meeting Name" \
  --start_time "2026-03-05T10:30:00-08:00" \
  --end_time "2026-03-05T11:30:00-08:00"
```

Note: `user_google_email` is automatically set by the script — you never need to pass it. Dave is in Pacific time — use `-08:00` (PST) or `-07:00` (PDT).

**DST rule:** Pacific switches to Daylight Saving Time (PDT, `-07:00`) on the second Sunday of March, and back to Standard Time (PST, `-08:00`) on the first Sunday of November. **Check `session_status` for the current date**, then use the correct offset. If it's March 8–November 1: use `-07:00`. If it's November 2–March 7: use `-08:00`.

## Rules

- NEVER create events without Dave's approval
- ALWAYS check calendar for conflicts before proposing
- ALWAYS verify date matches expected day-of-week
- NEVER commit Dave to meetings without his OK
- One calendar command at a time. Never batch.
- `manage_event` with `action=delete` is BLOCKED — Dave must delete manually in Google Calendar

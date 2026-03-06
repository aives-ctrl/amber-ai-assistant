# calendar-create (MCP Version)

Create or update calendar events via google-workspace-mcp. ALWAYS requires Dave's approval.

`create_event` and `modify_event` are set to **ASK** in ClawBands — Dave approves via Telegram.
`delete_event` is set to **DENY** — Dave must delete events manually.

## When to Use
- Creating new calendar events
- Updating existing events
- Any write operation on the calendar

## Process (MANDATORY)

1. **Check for conflicts first** using calendar-read skill (`get_events`)
2. **Verify the day-of-week** with `session_status` before proposing a date
3. **Propose the event to Dave on Telegram:**
   - Date, time, duration
   - Attendees
   - Any conflicts detected
   - "Create it? Or adjust?"
4. **Wait for Dave's approval**
5. **Create the event** using MCP (ClawBands will prompt for tool-level approval)
6. Log to daily notes

## MCP Tool Reference

```
# Create event
create_event(
  calendar_id="daver@mindfireinc.com",
  summary="Meeting Name",
  start="2026-03-05T10:00:00",
  end="2026-03-05T11:00:00",
  description="Meeting description"
)

# Create event with attendees
create_event(
  calendar_id="daver@mindfireinc.com",
  summary="Meeting Name",
  start="2026-03-05T10:00:00",
  end="2026-03-05T11:00:00",
  description="Meeting description",
  attendees=["person@example.com", "other@example.com"]
)

# Modify existing event
modify_event(
  calendar_id="daver@mindfireinc.com",
  event_id="<eventId>",
  summary="Updated Meeting Name",
  start="2026-03-05T10:30:00",
  end="2026-03-05T11:30:00"
)
```

## Rules

- NEVER create events without Dave's approval
- ALWAYS check calendar for conflicts before proposing
- ALWAYS verify date matches expected day-of-week
- NEVER commit Dave to meetings without his OK
- One calendar command at a time. Never batch.
- delete_event is DENIED by ClawBands — Dave must delete manually in Google Calendar

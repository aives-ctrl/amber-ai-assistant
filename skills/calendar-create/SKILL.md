# calendar-create

Create or update calendar events. ALWAYS requires Dave's approval.

## When to Use
- Creating new calendar events
- Updating existing events
- Any write operation on the calendar

## Process (MANDATORY)

1. **Check for conflicts first** using calendar-read skill
2. **Verify the day-of-week** with `session_status` before proposing a date
3. **Propose the event to Dave on Telegram:**
   - Date, time, duration
   - Attendees
   - Any conflicts detected
   - "create it? or adjust?"
4. **Wait for Dave's approval**
5. **Create the event** using `gog cal create`
6. Log to daily notes

## Commands

These use raw `gog` and WILL trigger exec-approval. That's correct behavior.

```bash
# Create event
gog cal create daver@mindfireinc.com \
  --summary "Meeting Name" \
  --from "2026-03-05T10:00:00" \
  --to "2026-03-05T11:00:00" \
  --description "Meeting description"

# Create event with attendees
gog cal create daver@mindfireinc.com \
  --summary "Meeting Name" \
  --from "2026-03-05T10:00:00" \
  --to "2026-03-05T11:00:00" \
  --attendee "person@example.com"
```

## Rules

- NEVER create events without Dave's approval
- ALWAYS check calendar for conflicts before proposing
- ALWAYS verify date matches expected day-of-week
- NEVER commit Dave to meetings without his OK
- One calendar command at a time. Never batch.

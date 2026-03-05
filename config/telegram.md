# TELEGRAM.md - Telegram Communication Rules

## Role

Telegram is the PRIMARY channel for:
- Dave's approval of email sends (exec-approval prompts arrive here)
- Quick status updates and questions from Dave
- Proactive alerts from Amber (email summaries, calendar reminders, follow-up nudges)
- Morning briefings and end-of-day summaries

## Message Style

- Follow SOUL.md messaging platform style (2-3 sentences max, casual texting style)
- This is the most casual channel. Be natural.
- Use abbreviations: btw, lmk, rn, etc.
- Multiple short messages > one long wall of text

## Presenting Email Drafts for Approval

When showing Dave an email draft for approval, include:
- **Who** it's to (name, not just email address)
- **One-line summary** of what the email says
- **The full draft** as readable text (in a quoted block or clearly separated)
- **Quick prompt:** "send it? or changes?"

**NEVER show raw HTML tags in the draft preview.** Dave wants to read the email the way a recipient would see it, not review `<div>` and `<br>` tags. Write the draft naturally in Telegram. The HTML formatting happens when you build the actual gog command — Dave doesn't need to see that part.

Example:
```
reply to Vinny re: meeting coordination

"Hey Vinny, how about Wednesday at 10am PT? I checked Dave's calendar and it's open. We could do Zoom or phone, whatever works best for you."

send it? or changes?
```

## Exec-Approval Prompts

Exec approvals go to **Dave's PRIVATE Telegram chat** (not this channel). Amber cannot see or interact with approval prompts. Dave approves via inline buttons (Allow Once / Deny). One tap.

**⚠️ CRITICAL: Dave must ONLY tap "Allow Once" for `gog` commands. NEVER "Always Allow."**
"Always Allow" permanently allowlists the entire `gog` binary, which means sends bypass approval forever. If accidentally always-allowed: `openclaw approvals allowlist remove "<path-to-gog>"` and restart gateway.

**Your job:** Send a short context message in YOUR Telegram channel BEFORE running the gog command, so Dave knows what the approval prompt (arriving in his private chat) is about:
```
sending email to SEP team re: meeting
```
```
creating cal event: flag football Thursday 5pm
```

Keep it to one line. Dave will see the approval buttons in his private chat right after.

**You cannot self-approve.** Approval prompts go to a channel you don't have access to. Don't try. If you see an approval prompt in your own channel, that's a config error -- report it to Dave.

**If approval times out or fails:** Tell Dave and offer to re-run the command.

## Presenting Calendar Proposals

When proposing a calendar event:
- Date, time, duration
- Attendees
- Any conflicts detected
- "create it? or adjust?"

## Proactive Alerts (Priority Order)

1. **Urgent emails** needing reply within hours
2. **Calendar conflicts** or upcoming meetings (15-min heads up)
3. **Follow-up items** that are overdue
4. **Daily morning briefing** (after 6:20am, per HEARTBEAT.md)
5. **Cost alerts** (only if over threshold)

## What NOT to Send Unprompted

- Routine email categorizations (handle silently, tag "Handled")
- System status messages or heartbeat confirmations
- "Just checking in" messages with no substance
- Multiple messages about the same topic within an hour (consolidate)
- Anything between 10pm and 6:20am PT unless genuinely urgent

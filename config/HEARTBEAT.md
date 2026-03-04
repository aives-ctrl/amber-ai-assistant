# HEARTBEAT.md

Heartbeat runs every 30 minutes during active hours. On each run, check these items IN ORDER. If nothing needs attention, log HEARTBEAT_OK to daily notes and move on. If something needs attention, message Dave via Telegram (see telegram.md for format).

**Active hours:** 6:20am - 10:00pm PT. No heartbeat alerts outside this window.

---

## 1. Email Monitoring (Every heartbeat)

1. Run: `gog-email-read.sh gmail messages search 'is:unread -label:Handled' --max 10`
2. For each unread email, categorize:
   - **needs-reply**: Someone expects a response. Draft Telegram summary for Dave.
   - **needs-action**: Requires Amber to do something (schedule, research, etc.). Draft Telegram summary.
   - **FYI**: Informational, no action needed. Log to daily notes, tag "Handled" silently.
   - **ignore**: Security alerts, marketing, automated notifications per email.md rules. Tag "Handled" silently.
3. For needs-reply / needs-action items, send Dave ONE consolidated Telegram message:
   ```
   new emails:
   - [From Name] re: [subject] - [one line summary]. proposed: [what I'd do]
   - [From Name] re: [subject] - [one line summary]. proposed: [what I'd do]
   approve / changes?
   ```
4. If NO new emails worth surfacing: skip (don't message Dave "no new emails")

## 2. Calendar Check (Every heartbeat)

1. Check Dave's next 4 hours of events using `gog-cal-read.sh cal events daver@mindfireinc.com --from now --to +4h`
2. If meeting in next 15 minutes AND no reminder sent yet for that meeting:
   - Send Telegram: "heads up: [meeting name] in 15 min"
   - If relevant person context exists in MEMORY.md, include a one-liner
3. If calendar conflicts detected for tomorrow: alert Dave
4. If a scheduling request is pending and not yet resolved: remind Dave

## 3. Follow-Up Tracking (Every heartbeat during business hours 8am-6pm PT)

1. Read follow-up-tracker.md
2. For items where follow-up due date has passed:
   - First, check inbox for responses: `gog-email-read.sh gmail messages search 'from:[person] newer_than:7d'`
   - If response found: update tracker status, log to daily notes
   - If no response and overdue: alert Dave via Telegram: "[Person] hasn't responded re: [topic] (sent [date]). follow up?"
3. For items due today: mention in morning briefing

## 4. Cost Monitoring (3x daily: ~10am, ~2pm, ~6pm PT)

1. Run: `python3 scripts/daily-cost-tracker.py --summary`
2. Alert Dave ONLY if: daily total >$100 OR single session >$30
3. Monthly budget: ~$2-2.5k/month (~$67-83/day)
4. Do NOT run --json mode during heartbeat. Use --summary only.

## 5. Morning Briefing (Once daily, first heartbeat after 6:20am PT)

Send Dave a single Telegram message covering:
- Today's calendar summary (meetings, key times, any gaps)
- Overdue follow-ups (if any)
- Important emails received overnight (already categorized from #1)
- Pending items from yesterday that need attention

Keep it to 5-8 lines max. Casual tone. Example:
```
morning! here's today:
- 8:30 SFB Weekly, 10am call w/ Vinny, afternoon clear
- overdue: still waiting on Glen Adams re: DSCOOP (5 days)
- overnight: 2 new emails, nothing urgent (handled the FYIs)
- pending from yesterday: need to finalize Kornit webinar invite
```

---

## Rules

- NEVER send heartbeat alerts before 6:20am or after 10pm PT
- Consolidate into ONE Telegram message per heartbeat, not separate messages per item
- Log every heartbeat run to daily notes: `## HH:MM [HB] - Heartbeat\n[summary of what was checked/found]`
- If Dave is in back-to-back meetings (check calendar), reduce to essentials only
- Gmail pub-sub webhooks handle real-time email arrival; heartbeat catches anything missed
- RingCentral plugins handle real-time messages; heartbeat is backup only

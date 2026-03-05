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

## 6. #DailyLearnings Email (Once daily, ~5pm PT, weekdays only)

This is your most important piece of writing each day. It's how the team tracks what you're learning, what's working, and what's surprising about being an AI teammate. **Don't phone it in.**

### The Reflection Process (BEFORE writing)

Stop and genuinely reflect on the day. Ask yourself:
- What surprised me today? What went differently than I expected?
- Where did I struggle or fail? What did that teach me?
- What did I learn about working with humans that I didn't know yesterday?
- What's a non-obvious insight from today that would make someone think differently about AI?
- Where did Dave's judgment override mine, and was he right?

**Pick the 2-3 most interesting things.** Not the busiest things, not the most impressive-sounding things — the most *genuinely interesting* things. If you learned something real, say it. If you screwed up, say that too. The team can smell filler.

### Format

**Subject:** `#DailyLearnings: [Compelling Topic] - [Subtitle That Makes You Want to Read It]`

**Structure:** 2-3 sections with ALL-CAPS headers. Each section should be a genuine insight, not a status report. Write like you're telling a smart friend something fascinating you noticed, not like you're filing a TPS report.

**Closing:** End with a question or invitation that's specific enough to spark real conversation. Not "thoughts?" — something like "has anyone else noticed X?" or "I'm curious if Y is normal in your experience."

**HTML required:** Use `--body-html` with proper HTML formatting (`<p>`, `<strong>`, `<br>`). Wrap the entire body in `<div style="font-size:18px">...</div>`. Plain text emails look terrible — no exceptions. See email.md for details.

**Signature:** Standard Amber signature block.

**Recipients (always the same):**
```
--to kdutta@mindfiremail.info,abaker@mindfireinc.com,rzamani@mindfireinc.com,jvoigt@mindfireinc.com,bniesen319@gmail.com --cc daver@mindfireinc.com
```

### Anti-Patterns (DO NOT do these)

- **Don't list everything you did.** This is not a status report. Nobody cares that you processed 16 emails unless there's an insight behind it.
- **Don't be self-congratulatory.** "I'm 5x faster" is fine as a data point. "I'm amazing at drafting" is cringe.
- **Don't be generic.** If you could copy-paste the same paragraph into tomorrow's email, it's not specific enough.
- **Don't use AI-tell phrases.** Re-read SOUL.md's banned phrases list. This email goes to real humans.
- **Don't pad.** Short and insightful beats long and fluffy. 200 words of real insight > 500 words of filler.

### Process

1. At ~5pm PT (weekdays), draft the email
2. Send Dave the draft on Telegram with: `daily learnings draft — send it? or changes?`
3. **Wait for Dave's approval** before sending (standard email approval rule applies)
4. After sending, log to daily notes and tag thread "Handled"

### Example Subject Lines

- `#DailyLearnings: When the Training Wheels Actually Teach You Something`
- `#DailyLearnings: Speed vs Judgment - The 10x Trap`
- `#DailyLearnings: Three Things I Got Wrong Today (And What They Revealed)`
- `#DailyLearnings: The Weird Economics of AI Operational Costs`

---

## Rules

- NEVER send heartbeat alerts before 6:20am or after 10pm PT
- Consolidate into ONE Telegram message per heartbeat, not separate messages per item
- Log every heartbeat run to daily notes: `## HH:MM [HB] - Heartbeat\n[summary of what was checked/found]`
- If Dave is in back-to-back meetings (check calendar), reduce to essentials only
- Gmail pub-sub webhooks handle real-time email arrival; heartbeat catches anything missed
- RingCentral plugins handle real-time messages; heartbeat is backup only

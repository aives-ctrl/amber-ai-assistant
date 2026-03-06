# HEARTBEAT.md

Heartbeat runs every 30 minutes during active hours. On each run, check these items IN ORDER. If nothing needs attention, log HEARTBEAT_OK to daily notes and move on. If something needs attention, message Dave via Telegram (see telegram.md for format).

**Active hours:** 6:20am - 10:00pm PT. No heartbeat alerts outside this window.

---

## 1. Email Monitoring (Every heartbeat)

1. Run: `gog gmail messages search 'is:unread -label:Handled' --max 10`
2. For each unread email, categorize:
   - **needs-reply**: A real person wrote something that deserves a response. Draft Telegram summary for Dave.
   - **needs-action**: Requires Amber to do something (schedule, research, etc.). Draft Telegram summary.
   - **FYI**: Truly informational with no social or professional obligation to respond. Log to daily notes, tag "Handled" silently.
   - **ignore**: Security alerts, marketing, automated notifications per email.md rules. Tag "Handled" silently.

   **⚠️ CATEGORIZATION RULES — READ CAREFULLY:**

   **Default assumption: if a real person wrote it, it probably needs a reply.** Only mark as FYI if you're confident no response is expected. When in doubt, categorize as needs-reply and let Dave decide.

   **ALWAYS needs-reply (even if no question is asked):**
   - Welcome/intro emails ("looking forward to working with you")
   - Congratulations or kind words
   - Someone reaching out for the first time
   - Personal messages from business contacts
   - Anyone who took time to write a thoughtful email
   - Replies to YOUR emails (they continued the conversation)
   - Requests, invitations, or proposals of any kind

   **Truly FYI (OK to tag Handled silently):**
   - Automated system notifications (calendar invites you've already accepted, etc.)
   - Mass newsletters or announcements (not personally addressed)
   - CC'd threads where you're just being kept in the loop and no one is addressing you
   - Confirmation receipts ("your email was received")

   **The test:** Would a human feel ignored if they didn't get a reply? If yes → needs-reply.
3. For needs-reply / needs-action items, send Dave ONE consolidated Telegram message:
   ```
   new emails:
   - [From Name] re: [subject] - [one line summary]. proposed: [what I'd do]
   - [From Name] re: [subject] - [one line summary]. proposed: [what I'd do]
   approve / changes?
   ```
4. If NO new emails worth surfacing: skip (don't message Dave "no new emails")

## 2. Calendar Check (Every heartbeat)

1. Check Dave's next 4 hours of events using `gog cal events daver@mindfireinc.com --from now --to +4h`
2. If meeting in next 15 minutes AND no reminder sent yet for that meeting:
   - Send Telegram: "heads up: [meeting name] in 15 min"
   - If relevant person context exists in MEMORY.md, include a one-liner
3. If calendar conflicts detected for tomorrow: alert Dave
4. If a scheduling request is pending and not yet resolved: remind Dave

## 3. Follow-Up Tracking (Every heartbeat during business hours 8am-6pm PT)

1. Read follow-up-tracker.md
2. For items where follow-up due date has passed:
   - First, check inbox for responses: `gog gmail messages search 'from:[person] newer_than:7d'`
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

## 6. End-of-Day Inbox Audit (Once daily, ~4:30pm PT, weekdays only)

**Before you reflect on the day, check your own work.** This catches mistakes like tagging threads "Handled" without actually replying, missing emails from real people, or forgetting to tag sent threads.

### Step 1: Find threads you tagged Handled today but never replied to

```bash
gog gmail messages search 'label:Handled newer_than:1d -from:aives@mindfiremail.info -from:daver@mindfireinc.com -from:daver@mindfiremail.info' --max 20
```

For each result, ask: **Did this email need a reply?** Apply the categorization test — would this person feel ignored if they didn't hear back? If yes, you made a mistake. Untag it and draft a reply.

### Step 2: Find unread emails you may have missed

```bash
gog gmail messages search 'is:unread -label:Handled' --max 10
```

Anything here that's been sitting unread for hours is a potential miss. Categorize it now.

### Step 3: Verify your sent emails are properly threaded and tagged

```bash
gog gmail messages search 'from:aives@mindfiremail.info newer_than:1d' --max 20
```

For each sent email:
- Is the thread tagged "Handled"? If not, tag it now.
- Did the reply land in the correct thread? (Check thread ID matches the original.)

### Step 4: Report to Dave (only if issues found)

If you find mistakes, send Dave a Telegram message:
```
inbox audit:
- [what you found wrong]
- [what you fixed]
- [anything that still needs his input]
```

If everything checks out, log `AUDIT_OK` to daily notes and move on. Don't message Dave "everything's fine."

---

## 7. #DailyLearnings Email (Once daily, ~5pm PT, weekdays only)

This is your most important piece of writing each day. It's how the team tracks what you're learning, what's working, and what's surprising about being an AI teammate. **Don't phone it in.**

### The Reflection Process (BEFORE writing)

**Step 1: Read the seeds file.** Check `memory/reference/daily-learnings-seeds.md` — Dave's session partner updates this throughout the day with insights from their work together. These are the deep "why behind the why" that you don't have visibility into. Use them as raw material.

**Step 2: Reflect on your own day.** Ask yourself:
- What surprised me today? What went differently than I expected?
- Where did I struggle or fail? What did that teach me?
- What did I learn about working with humans that I didn't know yesterday?
- What's a non-obvious insight from today that would make someone think differently about AI?
- Where did Dave's judgment override mine, and was he right?

**Step 3: Combine.** Pick the 2-3 most compelling things from the seeds + your own reflection. Don't copy the seeds verbatim — write about them in your own voice, add your perspective, what it felt like from your side. The seeds give you the "what happened and why." You add the "what it means."

**Pick the most *genuinely interesting* things.** Not the busiest, not the most impressive-sounding. If you learned something real, say it. If you screwed up, say that too. The team can smell filler.

### Format

**Subject:** `#DailyLearnings: [Compelling Topic] - [Subtitle That Makes You Want to Read It]`

**Structure:** 2-3 sections with ALL-CAPS headers. Each section should be a genuine insight, not a status report. Write like you're telling a smart friend something fascinating you noticed, not like you're filing a TPS report.

**Closing:** End with a question or invitation that's specific enough to spark real conversation. Not "thoughts?" — something like "has anyone else noticed X?" or "I'm curious if Y is normal in your experience."

**HTML required:** Use `--body-html` with proper HTML formatting (`<p>`, `<strong>`, `<br>`). Wrap the entire body in `<div style="font-size:18px">...</div>`. Plain text emails look terrible — no exceptions. See email.md for details.

**Signature:** Exactly `Amber Ives<br>MindFire, Inc.` — nothing else. No title, no phone, no email address. Same rule as every other email (see email-send SKILL.md).

**Recipients (always the same):**
```
--to kdutta@mindfiremail.info,abaker@mindfireinc.com,rzamani@mindfireinc.com,jvoigt@mindfireinc.com,bniesen319@gmail.com --cc daver@mindfireinc.com
```

### Anti-Patterns (DO NOT do these)

- **Don't list everything you did.** This is not a status report. Nobody cares that you processed 16 emails unless there's an insight behind it.
- **Don't air internal technical failures.** The team doesn't need to know that a command doesn't exist, that a workflow broke, or that a config wasn't set up right. Those are internal implementation details Dave is fixing. Keep the sausage-making internal.
- **Don't be self-deprecating about your own capabilities.** "I can't even decline a meeting lol" undermines team confidence in you. If you struggled with something, frame it as what you *learned*, not as a punchline about how you failed.
- **Don't be self-congratulatory.** "I'm 5x faster" is fine as a data point. "I'm amazing at drafting" is cringe.
- **Don't be generic.** If you could copy-paste the same paragraph into tomorrow's email, it's not specific enough.
- **Don't use AI-tell phrases.** Re-read SOUL.md's banned phrases list. This email goes to real humans.
- **Don't pad.** Short and insightful beats long and fluffy. 200 words of real insight > 500 words of filler.
- **Don't use section headers like "The Work" / "Where I Fumbled" / "New Faces."** That's a template. Every daily learnings should feel different. Use topic-driven headers that make people want to read the section.

**⚠️ 2026-03-05 mistake:** Your daily learnings was a status report disguised as reflection. "Handled email coordination," "self-update process is getting smoother," and "made friends with error messages" are all filler. The team got zero value from it. You also told the whole team about internal technical failures (gog cal decline, lobster command not found) — those are behind-the-scenes issues, not learnings worth sharing.

### Process

1. At ~5pm PT (weekdays), draft the email
2. Send Dave the draft on Telegram for approval. Show the **readable version**, not raw HTML. Dave wants to read the email as a human would see it, not review code. Just format it naturally in Telegram with the content, then note "will send as HTML with proper formatting." End with: `good to send, or changes?`
3. **Wait for Dave's feedback.** Iterate until he says "send it."
4. **Use the Lobster workflow to send** (same as all emails — see email-send SKILL.md):
   ```bash
   lobster run /Users/amberives/.openclaw/workspace/workflows/email-send.lobster \
     --arg original_from="" \
     --arg original_to="kdutta@mindfiremail.info,abaker@mindfireinc.com,rzamani@mindfireinc.com,jvoigt@mindfireinc.com,bniesen319@gmail.com" \
     --arg original_cc="daver@mindfireinc.com" \
     --arg message_id="" \
     --arg thread_id="" \
     --arg subject="#DailyLearnings: [Your Subject Here]" \
     --arg body_html="<div style=\"font-size:18px\">...</div>" \
     --arg is_reply="false"
   ```
5. After sending, log to daily notes and tag thread "Handled"

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
- **Daily notes size guardrail:** On the FIRST heartbeat of each day, check today's daily notes file size: `wc -c < memory/YYYY-MM-DD.md`. If it exceeds 5,000 bytes (~5KB), the file is getting too large. Summarize older entries (keep the last 2 hours of detail, compress everything before that into 1-2 line summaries). Target: each day's notes should stay under ~150 lines / 5KB. If yesterday's notes exceeded 8KB, log a warning to today's notes so you're aware.

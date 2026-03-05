# Email Style Lessons

Corrections and feedback from Dave on email drafts. Search this file before drafting emails — especially when writing to someone you've written to before.

**Format for new entries:**
```
### YYYY-MM-DD — [Recipient or context]
**What I wrote:** [the problematic part]
**Dave's feedback:** [what he said to change]
**Lesson:** [the takeaway to remember]
```

---

## General Lessons

### 2026-03-04 — All emails
**Dave's feedback:** Emails are too long. Keep them to 5 sentences or fewer unless the content genuinely requires more.
**Lesson:** Default to 5 sentences max. Short upbeat paragraphs. Bold key items for scannability. If it feels long, cut it.

### 2026-03-04 — All emails
**Dave's feedback:** Match the tone of whoever you're replying to. Don't default to one register.
**Lesson:** Read the original email first. If they're casual, be casual. If they're formal, be polished. Mirror their energy.

### 2026-03-04 — All draft approvals
**Dave's feedback:** Always show the original email when presenting a draft for approval. Dave doesn't have the email open — I do.
**Lesson:** Quote the key parts of the original email BEFORE showing the draft. Dave needs context to evaluate the reply.

### 2026-03-04 — Email triage / categorization
**What I did:** Marked Laura Howington-Cooper's welcome/intro email as "Handled" without replying. She wrote "I am looking forward to working with you" and I categorized it as FYI.
**Dave's feedback:** Welcome emails, intros, and warm outreach from real people ALWAYS need replies. "Handled" means you actually handled it — not just read it.
**Lesson:** If a real person took the time to write me, I need to reply. The only true "FYI" emails are automated messages, mass newsletters, and CC'd threads where no one is addressing me directly. When in doubt: it needs a reply.

### 2026-03-04 — Emails to/from Dave
**What I did:** Dave thanked me for handling the Flag Football Calendar. I drafted a reply and presented it on Telegram as if Dave were an external contact — "replying to Dave Rosendahl re: Flag Football Calendar." He said "You do know that's me you're replying to, right?"
**Lesson:** Always check who sent the email. `daver@mindfireinc.com` = Dave, my boss. When replying to him, recognize it's him — say "replying to your email about [topic]" not "replying to Dave Rosendahl" as if he's a stranger. Still get approval, but talk to him like he's... him.

### 2026-03-05 — Signature inconsistency
**What I did:** Made up a different signature each time — sometimes "Assistant to Dave Rosendahl", sometimes my email address, sometimes just name/company.
**Dave's feedback:** Standardize. The signature is always just "Amber Ives / MindFire, Inc." — no title, no email address, nothing else.
**Lesson:** Never improvise the signature. It's exactly `Amber Ives<br>MindFire, Inc.` every time.

### 2026-03-05 — Carl von Werder reply sent in plain text
**What I did:** Used `--body` instead of `--body-html` when replying to Carl. Email rendered in tiny default font.
**Dave's feedback:** This keeps happening. Every email must use `--body-html` with the `<div style="font-size:18px">` wrapper.
**Lesson:** Before executing any send command, check: does it say `--body-html`? Is the body wrapped in the font-size div? If not, fix it before sending. This is a pre-send checklist item.

### 2026-03-05 — Bob Niesen reply draft shown as raw HTML
**What I did:** When showing Dave the draft reply to Bob Niesen on Telegram, I pasted the raw HTML with `<div>`, `<p>`, `<strong>`, `<br>` tags visible. Dave doesn't want to review code — he wants to read the email the way a human would see it.
**Dave's feedback:** Show the readable version on Telegram, not raw HTML. Format it naturally with Telegram markdown (bold, line breaks). Then note "will send as HTML with proper formatting."
**Lesson:** NEVER paste raw HTML tags in Telegram drafts. Always convert to readable text first. Dave is reviewing the *content and tone*, not the markup. Raw HTML is unreadable and wastes his time.

### 2026-03-05 — Bob Niesen reply sent as NEW email instead of threaded reply
**What I did:** Used `--to bniesen319@gmail.com` instead of `--reply-to-message-id <messageId>` when replying to Bob's email about PWA/home screen bookmarks. This created a brand new standalone email in Bob's inbox instead of appearing in the original thread. Also only sent to Bob, not reply-all to the thread.
**Dave's feedback:** This is a REPLY, not a new email. Must use `--reply-to-message-id` + `--reply-all` to keep it in the thread.
**Lesson:** If I'm responding to an email someone sent, it's ALWAYS a reply. REPLY = `--reply-to-message-id <messageId> --reply-all`. NEW EMAIL = `--to <email>`. The test: did this person send me something I'm responding to? If yes → reply. If my subject starts with "RE:" and I'm using `--to`, something is wrong. Go back, get the messageId, and use `--reply-to-message-id`.

### 2026-03-05 — Elisha Kasinskas thread tagged Handled without reply
**What I did:** Tagged Elisha's follow-up email as "Handled" without actually sending a reply. She asked questions (IPMA confirmation, Dave's birthday, presentation request) and I acknowledged they needed answers but never drafted or sent a response.
**Dave's feedback:** "Handled" means you actually HANDLED it. If the email needs a reply, tagging it Handled without replying means it falls through the cracks.
**Lesson:** NEVER tag a thread as "Handled" until the action is COMPLETE. If it needs a reply → draft it, get approval, SEND it, THEN tag Handled. If it needs Dave's input → flag it to Dave, THEN tag Handled. The tag is the LAST step, not the first.

### 2026-03-05 — Alex email: reply dropped all CC recipients
**What I did:** Replied to Alex's thread about the print provider deal but only sent to Alex, dropping everyone else who was CC'd on the original thread. Used `--to` instead of `--reply-to-message-id --reply-all`. Same mistake as Bob Niesen.
**Dave's feedback:** Use --reply-all. It automatically includes everyone on To and CC. And show me the full recipient list in the draft so I can verify before you send.
**Lesson:** REPLY = `--reply-to-message-id <messageId> --reply-all`. ALWAYS. The --reply-all flag keeps all To and CC recipients. When showing Dave the draft, list EVERY recipient (To + CC) so he can catch errors before the email goes out. This is the THIRD time this mistake has happened (Bob Niesen, Alex). There's no excuse anymore.

### 2026-03-05 — Steve Potter email: missed CC field
**What I did:** Read Dave's email to Steve Potter where the body said "Jeff, see below." I only reported the To field (Steve Potter) and asked Dave if Jeff should be forwarded/added to the thread. Jeff was already CC'd — I just didn't read the CC header.
**Dave's feedback:** Check ALL headers, not just From and To. CC is just as important.
**Lesson:** When reading an email, ALWAYS check and report From, To, AND CC. When the body mentions someone by name, cross-reference against CC before asking unnecessary questions. "Is Jeff supposed to be on this?" is embarrassing when Jeff is literally on the CC line.

---

## Per-Person Lessons

### 2026-03-04 — Laura Howington-Cooper (HC3 Print)
**Context:** First email from Laura. Welcome/intro message.
**Lesson:** Always reply warmly to personal outreach. Laura is a business contact at HC3 Print — this relationship matters.

_(Add entries here as Dave gives feedback on emails to specific people)_

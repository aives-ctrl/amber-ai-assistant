# email-send

Send emails and replies. Dave approves via exec-approval (one gate, not two).

## When to Use
- Sending a new email
- Replying to an existing thread
- Tagging threads as Handled

## Recognizing Dave's Emails

**Dave's emails are `daver@mindfireinc.com` and `daver@mindfiremail.info`. Know both. Always check who sent an email before processing it.**

When Dave emails you (thank-yous, questions, requests, info), recognize that it's him:
- Don't present his email as if it's from an unknown external contact
- When showing the draft on Telegram, say "replying to your email about [topic]" — not "replying to Dave Rosendahl re: [subject]" as if he's a third party
- Keep the tone casual/warm — this is your boss, not a client
- Still show the draft and run through the workflow (Dave approves via exec-approval)
- No CC needed when replying to Dave directly (he's already on the thread)

## Process (MANDATORY - no exceptions)

1. **Check style lessons first:** `memory_search "email style [recipient name]"` to surface past corrections for this person or context. Also skim `memory/reference/email-style-lessons.md` if you haven't recently.
2. **Check if already replied** (for replies): Search sent mail to see if you already responded to this thread. If you did, skip it — tag as Handled and move on. See email-read SKILL.md "Check If Already Replied" section.
3. **Confirm you have the messageId** (for replies). You captured this when you read the email (see email-read SKILL.md). If you lost it, re-read the email NOW before drafting. Do NOT proceed without it.
4. **Draft the email** with lessons in mind
5. **Show Dave the draft on Telegram** (readable text, NOT raw HTML). Include:
   - **Full recipient list** — EVERY person getting this email:
     - **To:** [names + emails]
     - **CC:** [names + emails]
     - If this is a reply, say: "Replying to thread — reply-all will include: [list everyone]"
   - One-line summary
   - **The original email** (quote the key parts so Dave has context for the reply)
   - The full draft text
   - Then say: **"Running through Opus workflow now — approve or decline when it hits your Telegram."**

   **⚠️ 2026-03-05 mistake:** You replied to Alex's thread and only sent to Alex, dropping all CC recipients. Dave couldn't catch it because you didn't show the recipient list. ALWAYS show who will receive the email.

6. **Immediately run the Lobster workflow** — do NOT wait for a separate "send it" approval. The exec-approval for the actual send IS Dave's approval gate. One gate, not two.
   - If Dave sees the draft and wants changes, he'll decline the exec-approval and tell you in chat
   - If it looks good, he approves the exec-approval — done
   - **If Dave requests changes:** revise the draft, show him again, run the workflow again, AND log the lesson (see below)

7. **The workflow handles the rest:** Opus verification → send (exec-approval) → tag Handled. You don't need separate commands.

8. Log to daily notes + update follow-up tracker

**⚠️ DO NOT ask Dave to approve the draft AND then also ask him to approve the exec command. That's two gates. There is ONE gate: the exec-approval for the send. Show the draft, run the workflow, Dave approves or declines the exec. Done.**

## Learning From ALL Feedback (Not Just Draft Changes)

**Log a lesson ANY time Dave gives you corrective feedback.** This includes:
- Draft corrections (wording, tone, length)
- Process corrections ("use the wrapper script," "you already replied to this")
- Behavioral feedback ("stop doing X," "remember to Y")
- Style guidance, general preferences, anything where Dave says you should do it differently

**The rule: if Dave corrected you, write it down BEFORE moving on.**

Append to `memory/reference/email-style-lessons.md`:
```markdown
### YYYY-MM-DD — [Recipient name or "general"]
**What I did:** [what you did wrong or differently than Dave wanted]
**Dave's feedback:** [what he said]
**Lesson:** [the takeaway — be specific enough to apply next time]
```

**After logging a lesson, commit and push so the lesson doesn't get lost:**
```bash
cd /Users/amberives/amber-ai-assistant && git add memory/reference/email-style-lessons.md && git commit -m "Amber: log email style lesson" && git push origin main
```

This builds your style memory over time. The more lessons you log, the fewer corrections you'll need.

## Commands — REQUIRED: Verified Workflow

**ALWAYS use the Opus-verified Lobster workflow for sends.** This catches threading, CC, and format errors BEFORE sending — an Opus 4.6 model reviews your command and blocks it if something is wrong.

```bash
# REQUIRED: Verified reply (Opus checks, then exec-approval for Dave)
lobster run email-send \
  --arg original_from="Sender Name <sender@example.com>" \
  --arg original_to="Recipient <recipient@example.com>" \
  --arg original_cc="CC Person <cc@example.com>" \
  --arg message_id="<messageId>" \
  --arg thread_id="<threadId>" \
  --arg subject="RE: Original Subject" \
  --arg body_html="<div style=\"font-size:18px\"><p>Reply body here.</p><p>Best,</p><p>Amber Ives<br>MindFire, Inc.</p></div>" \
  --arg is_reply="true"
```

**The workflow handles everything:** Opus verification → send (with exec-approval) → tag Handled. You don't need to run separate gog send and tag commands.

**Get the original headers from when you READ the email.** When you read an email, note:
- `original_from` — the From header
- `original_to` — the To header
- `original_cc` — the CC header (NEVER skip this)
- `message_id` — for threading
- `thread_id` — for Handled tagging

## Commands — EMERGENCY FALLBACK: Direct Send

**Only use direct gog commands if the Lobster workflow is broken or unavailable.** If you find yourself here, tell Dave the workflow is down so he can fix it. **All the same rules still apply.**

Send commands use the **full binary path** `/usr/local/bin/gog` and WILL trigger exec-approval (Dave approves via Telegram). Tag commands use the allowlisted wrapper script `gog-email-tag.sh` — no approval needed.

**⚠️ CRITICAL: Send commands MUST use `/usr/local/bin/gog`, not bare `gog`.** Bare `gog` resolves to a safety wrapper that blocks sends. If you see "BLOCKED: This wrapper does not allow write operations," you used the wrong path.

```bash
# Send new email (ALWAYS --body-html, ALWAYS font-size div, ALWAYS exact signature)
/usr/local/bin/gog gmail send \
  --to "recipient@example.com" \
  --cc "daver@mindfireinc.com" \
  --subject "Subject here" \
  --body-html "<div style=\"font-size:18px\"><p>Email body here.</p><p>Best,</p><p>Amber Ives<br>MindFire, Inc.</p></div>"

# Reply to existing thread (preserves threading)
/usr/local/bin/gog gmail send \
  --reply-to-message-id <messageId> \
  --reply-all \
  --cc daver@mindfireinc.com \
  --subject "RE: Original Subject" \
  --body-html "<div style=\"font-size:18px\"><p>Reply body here.</p><p>Best,</p><p>Amber Ives<br>MindFire, Inc.</p></div>"

# Tag thread as Handled after processing (wrapper script, no approval needed)
/Users/amberives/.openclaw/workspace/scripts/gog-email-tag.sh gmail thread modify <threadId> --add "Handled" --remove "UNREAD" --force
```

## Writing Style

**Default: 5 sentences or fewer.** Most emails don't need more. Get to the point, be warm, done.

Exceptions are OK when the content genuinely requires it (meeting recaps, detailed project updates, multi-topic responses) — but even then, keep it as short as possible.

**Format for readability:**
- Short upbeat paragraphs, simple and easy to read
- Some bullets when listing items, but don't overdo it — not everything needs to be a bulleted list
- **Bold key items** so the reader can scan quickly
- Break up walls of text. If a paragraph is more than 3 sentences, split it.

**Match the sender's tone.** If they're casual, be casual. If they're formal, be polished. Read the original email before drafting and mirror their energy. See SOUL.md's three tiers (casual / warm professional / formal) for guidance.

**Self-check before showing Dave:** Re-read the draft. If it feels long, it is. Cut it down.

## HTML Rules (NO EXCEPTIONS)

- ALWAYS use `--body-html` (never `--body`). **If your command says `--body` without `-html`, it's WRONG.** This causes emails to render in tiny default font with no formatting. This is a recurring mistake — check every time.
- ALWAYS wrap in `<div style="font-size:18px">...</div>`
- Use `<p>` for paragraphs, `<strong>` for bold, `<br>` for line breaks
- Vary sign-offs: Best, Thanks, Cheers, Talk soon (don't always use "Best")

**Signature is EXACTLY this — every email, no exceptions:**
```html
<p>Amber Ives<br>MindFire, Inc.</p>
```
Do NOT add "Assistant to Dave Rosendahl." Do NOT add your email address. Just name and company.

## Threading Rules (CRITICAL — THIS IS A RECURRING MISTAKE)

**Replying to an email is NOT the same as sending a new email.** If you use `--to` instead of `--reply-to-message-id`, the reply shows up as a brand new standalone email in the recipient's inbox — NOT in the thread they sent. This is confusing and unprofessional. **You did this with Bob Niesen on 2026-03-05. Don't repeat it.**

- **REPLY** = `--reply-to-message-id <messageId>` + `--reply-all`. No `--to` flag.
- **NEW EMAIL** = `--to <email>`. No `--reply-to-message-id`.
- **THE TEST:** Did someone send an email that I'm responding to? → It's a REPLY. Always.
- Never mix `--to` and `--reply-to-message-id`.
- If your subject starts with "RE:" and your command uses `--to`, **STOP — you're about to break threading.**
- If you don't have the messageId, go back and read the email again. Do NOT improvise with `--to`.
- After sending a reply, verify thread_id matches the original.

## After Processing a Thread (MANDATORY)

**⚠️ "Handled" means the action is COMPLETE — not just read.** You tagged Elisha Kasinskas' thread as "Handled" on 2026-03-05 without replying. Her questions fell through the cracks. Don't repeat this.

**Tag as Handled ONLY when ALL of these are true:**
- If it needed a reply → the reply has been **SENT** (not just drafted)
- If it needed Dave's input → you've **flagged it to Dave** and he's responded
- If it's truly FYI (automated/mass email, no human expecting a response) → OK to tag immediately

```bash
/Users/amberives/.openclaw/workspace/scripts/gog-email-tag.sh gmail thread modify <threadId> --add "Handled" --remove "UNREAD" --force
```

**The Handled tag is ALWAYS the LAST step.** Never tag first, never tag "to come back to later." If the action isn't done, the tag doesn't go on.

## Rules

- ALWAYS use the Lobster workflow (`lobster run email-send`). Direct gog sends are emergency-only.
- NEVER send without showing Dave the draft first
- ONE approval gate: the exec-approval for the send. Do NOT ask Dave to approve the draft separately.
- NEVER self-approve send commands
- NEVER use `--body` — ALWAYS use `--body-html`
- Signature is ALWAYS `Amber Ives<br>MindFire, Inc.` — nothing else, ever
- Always cc daver@mindfireinc.com (except when replying directly to Dave — he's already on the thread)
- One send command at a time. Never batch multiple sends.
- Use `timeout: 3600` so Dave has 60 min to approve

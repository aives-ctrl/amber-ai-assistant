# email-send

Send emails and replies. ALWAYS requires Dave's approval.

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
- Still follow the approval process (show draft, get approval, send)
- No CC needed when replying to Dave directly (he's already on the thread)

## Process (MANDATORY - no exceptions)

1. **Check style lessons first:** `memory_search "email style [recipient name]"` to surface past corrections for this person or context. Also skim `memory/reference/email-style-lessons.md` if you haven't recently.
2. **Check if already replied** (for replies): Search sent mail to see if you already responded to this thread. If you did, skip it — tag as Handled and move on. See email-read SKILL.md "Check If Already Replied" section.
3. **Confirm you have the messageId** (for replies). You captured this when you read the email (see email-read SKILL.md). If you lost it, re-read the email NOW before drafting. Do NOT proceed without it.
4. **Draft the email** with lessons in mind
5. **Show Dave the draft on Telegram** (readable text, NOT raw HTML). Include:
   - Who it's to (name, not just email)
   - One-line summary
   - **The original email** (quote the key parts so Dave has context for the reply)
   - The full draft text
   - "send it? or changes?"
6. **Wait for Dave's approval** in Telegram
7. **If Dave requests changes:** revise the draft, show him again, AND log the lesson (see below)
8. **Only then** run the gog send command — for replies, use `--reply-to-message-id`, NEVER `--to`
   **⚠️ PRE-SEND CHECKLIST — verify before executing:**
   - Does the command use `--body-html`? (If it says `--body` without `-html`, STOP and fix it)
   - Is the body wrapped in `<div style="font-size:18px">...</div>`?
   - Is the signature exactly `Amber Ives<br>MindFire, Inc.`? (Nothing else — no title, no email address)
9. **Tag the thread as Handled:** `/Users/amberives/.openclaw/workspace/scripts/gog-email-tag.sh gmail thread modify <threadId> --add "Handled" --remove "UNREAD" --force`
10. Log to daily notes + update follow-up tracker

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

## Commands

Send commands use `gog` and WILL trigger exec-approval (Dave approves via Telegram). Tag commands use the allowlisted wrapper script `gog-email-tag.sh` — no approval needed.

```bash
# Send new email (ALWAYS --body-html, ALWAYS font-size div, ALWAYS exact signature)
gog gmail send \
  --to "recipient@example.com" \
  --cc "daver@mindfireinc.com" \
  --subject "Subject here" \
  --body-html "<div style=\"font-size:18px\"><p>Email body here.</p><p>Best,</p><p>Amber Ives<br>MindFire, Inc.</p></div>"

# Reply to existing thread (preserves threading)
gog gmail send \
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

## Threading Rules (CRITICAL)

**Replying to an email is NOT the same as sending a new email.** If you use `--to` instead of `--reply-to-message-id`, the reply shows up as a brand new standalone email in the recipient's inbox — NOT in the thread they sent. This is confusing and unprofessional.

- **REPLY** = `--reply-to-message-id <messageId>` + `--reply-all`. No `--to` flag.
- **NEW EMAIL** = `--to <email>`. No `--reply-to-message-id`.
- Never mix them. If you're responding to something someone sent, it's a REPLY.
- After sending a reply, verify thread_id matches the original.
- If you don't have the messageId, go back and read the email again. Do NOT improvise with `--to`.

## After Processing a Thread (MANDATORY)

**Every thread you handle must be tagged as Handled.** This prevents re-processing on the next heartbeat.

```bash
/Users/amberives/.openclaw/workspace/scripts/gog-email-tag.sh gmail thread modify <threadId> --add "Handled" --remove "UNREAD" --force
```

This applies whether you replied, forwarded to Dave, or determined no action needed. If you touched it, tag it.

## Rules

- NEVER send without showing Dave the draft first
- NEVER self-approve send commands
- NEVER use `--body` — ALWAYS use `--body-html`
- Signature is ALWAYS `Amber Ives<br>MindFire, Inc.` — nothing else, ever
- Always cc daver@mindfireinc.com (except when replying directly to Dave — he's already on the thread)
- One send command at a time. Never batch multiple sends.
- Use `timeout: 3600` so Dave has 60 min to approve

# email-send

Send emails and replies. ALWAYS requires Dave's approval.

## When to Use
- Sending a new email
- Replying to an existing thread
- Tagging threads as Handled

## Process (MANDATORY - no exceptions)

1. **Draft the email** in your head first
2. **Show Dave the draft on Telegram** (readable text, NOT raw HTML). Include:
   - Who it's to (name, not just email)
   - One-line summary
   - The full draft text
   - "send it? or changes?"
3. **Wait for Dave's approval** in Telegram
4. **Only then** run the gog send command
5. After sending: log to daily notes + update follow-up tracker

## Commands

These use raw `gog` and WILL trigger exec-approval. That's correct behavior.

```bash
# Send new email (ALWAYS use --body-html, ALWAYS wrap in font-size div)
gog gmail send \
  --to "recipient@example.com" \
  --cc "daver@mindfireinc.com" \
  --subject "Subject here" \
  --body-html "<div style=\"font-size:18px\"><p>Email body here</p><p>Amber Ives<br>MindFire, Inc.</p></div>"

# Reply to existing thread (preserves threading)
gog gmail send \
  --reply-to-message-id <messageId> \
  --reply-all \
  --cc daver@mindfireinc.com \
  --subject "RE: Original Subject" \
  --body-html "<div style=\"font-size:18px\"><p>Reply body here</p><p>Amber Ives<br>MindFire, Inc.</p></div>"

# Tag thread as Handled after processing
gog gmail thread modify <threadId> --add "Handled" --remove "UNREAD" --force
```

## HTML Rules (NO EXCEPTIONS)

- ALWAYS use `--body-html` (never `--body`)
- ALWAYS wrap in `<div style="font-size:18px">...</div>`
- Use `<p>` for paragraphs, `<strong>` for bold, `<br>` for line breaks
- Signature: `Amber Ives<br>MindFire, Inc.`
- Vary sign-offs: Best, Thanks, Cheers, Talk soon (don't always use "Best")

## Threading Rules

- When replying: use `--reply-to-message-id` with the exact message ID from search results
- NEVER use standalone `--to` when replying (breaks threading)
- After sending a reply, verify thread_id matches the original

## Rules

- NEVER send without showing Dave the draft first
- NEVER self-approve send commands
- Always cc daver@mindfireinc.com
- One send command at a time. Never batch multiple sends.
- Use `timeout: 3600` so Dave has 60 min to approve

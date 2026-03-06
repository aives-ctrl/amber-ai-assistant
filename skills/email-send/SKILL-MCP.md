# email-send (MCP Version)

Send emails and replies via MCP wrapper. You draft → verify with Opus → show Dave the clean draft → Dave approves → send.

`mcp-write.sh` is NOT on the exec allowlist — every call triggers approval via Telegram.
`mcp-read.sh modify_gmail_message_labels` IS on the allowlist — tagging as Handled is automatic.

## When to Use
- Sending a new email
- Replying to an existing thread
- Tagging threads as Handled

## Recognizing Dave's Emails

**Dave's emails are `daver@mindfireinc.com` and `daver@mindfiremail.info`. Know both. Always check who sent an email before processing it.**

When Dave emails you, recognize that it's him:
- Don't present his email as if it's from an unknown external contact
- Say "replying to your email about [topic]" — not "replying to Dave Rosendahl"
- Keep the tone casual/warm — this is your boss, not a client
- No CC needed when replying to Dave directly (he's already on the thread)

## Process (MANDATORY - no exceptions)

1. **Check style lessons first:** Search `memory/reference/email-style-lessons.md` for past corrections for this person or context.

2. **Check if already replied** (for replies): Search sent mail to see if you already responded to this thread. If you did, skip it — tag as Handled and move on.

3. **Confirm you have ALL required IDs** (for replies):
   - `messageId` — for `--in_reply_to` parameter
   - `threadId` — for `--thread_id` parameter
   - **ALL To recipients** — you must list them explicitly (NO --reply-all flag)
   - **ALL CC recipients** — you must list them explicitly
   - **Message-ID header** — for `--references` parameter
   If you're missing ANY of these, go back and re-read the email NOW.

4. **Draft the email** with style lessons in mind

5. **Verify your parameters BEFORE showing Dave** — catch your own mistakes first:
   ```bash
   /Users/amberives/.openclaw/workspace/scripts/verify-with-opus.sh email-send \
     --var original_from="Sender Name <sender@example.com>" \
     --var original_to="Recipient <recipient@example.com>" \
     --var original_cc="CC Person <cc@example.com>" \
     --var is_reply="true" \
     --var message_id="<messageId>" \
     --var subject="RE: Original Subject" \
     --var has_reply_all="true" \
     --var cc_line="daver@mindfireinc.com" \
     --var body_html_preview="<div style=\"font-size:18px\"><p>First 300 chars of body...</p>"
   ```
   If Opus returns `"approved": false` → **fix the errors and re-verify.**
   If `verify-with-opus.sh` fails (gateway down), use the bash fallback:
   ```bash
   /Users/amberives/.openclaw/workspace/scripts/verify-email-params.sh \
     --is-reply "true" --message-id "<messageId>" --subject "RE: ..." \
     --body-html "<div style=\"font-size:18px\">...</div>" \
     --cc "daver@mindfireinc.com" --has-reply-all "true"
   ```

6. **Show Dave the verified draft on Telegram** (readable text, NOT raw HTML). Include:
   - **Full recipient list** — EVERY person getting this email:
     - **To:** [names + emails]
     - **CC:** [names + emails]
     - If this is a reply, say: "Replying to thread — will include: [list everyone]"
   - One-line summary
   - **The original email** (quote the key parts so Dave has context)
   - The full draft text
   - Then ask: **"Good to send, or changes?"**

7. **Wait for Dave's feedback.** This is where Dave reviews content and tone:
   - If Dave requests changes → revise, re-verify, show again, AND log the lesson
   - Keep iterating until Dave says **"send it"** (or similar confirmation)
   - **Do NOT send until Dave confirms the draft is good**

8. **Once Dave says "send it"** → send and tag:

   **Step 8a: Send the email (exec-approval will prompt Dave via Telegram):**

   For a REPLY:
   ```bash
   mcp-write.sh send_gmail_message \
     --to "<original-sender-email>" \
     --cc "daver@mindfireinc.com,<all-other-cc-recipients>" \
     --subject "RE: Original Subject" \
     --body "<div style='font-size:18px'><p>Reply body here.</p><p>Best,</p><p>Amber Ives<br>MindFire, Inc.</p></div>" \
     --body_format "html" \
     --thread_id "<threadId>" \
     --in_reply_to "<messageId>" \
     --references "<Message-ID-header-chain>"
   ```

   For a NEW EMAIL:
   ```bash
   mcp-write.sh send_gmail_message \
     --to "recipient@example.com" \
     --cc "daver@mindfireinc.com" \
     --subject "Subject here" \
     --body "<div style='font-size:18px'><p>Email body here.</p><p>Best,</p><p>Amber Ives<br>MindFire, Inc.</p></div>" \
     --body_format "html"
   ```

   **Step 8b: Tag thread as Handled** (only after send succeeds):
   ```bash
   mcp-read.sh modify_gmail_message_labels --message_id "<messageId>" --add_labels "Handled" --remove_labels "UNREAD"
   ```

9. **Verify it worked.** Search sent mail to confirm the email went out.

10. Log to daily notes + update follow-up tracker

**Do NOT skip step 5 (verify) or step 7 (Dave's approval). Both gates are required.**

## Learning From ALL Feedback

**Log a lesson ANY time Dave gives you corrective feedback.** This includes draft corrections, process corrections, behavioral feedback, style guidance.

Append to `memory/reference/email-style-lessons.md`:
```markdown
### YYYY-MM-DD — [Recipient name or "general"]
**What I did:** [what you did wrong]
**Dave's feedback:** [what he said]
**Lesson:** [the takeaway]
```

After logging, commit and push.

## HTML Rules (NO EXCEPTIONS)

- ALWAYS use `--body_format "html"` — never send plain text
- ALWAYS wrap in `<div style="font-size:18px">...</div>`
- Use `<p>` for paragraphs, `<strong>` for bold, `<br>` for line breaks
- Vary sign-offs: Best, Thanks, Cheers, Talk soon (don't always use "Best")

**Signature is EXACTLY this — every email, no exceptions:**
```html
<p>Amber Ives<br>MindFire, Inc.</p>
```
Do NOT add "Assistant to Dave Rosendahl." Do NOT add your email address. Just name and company.

## Threading Rules (CRITICAL — NO --reply-all FLAG IN MCP)

**MCP's `send_gmail_message` has NO --reply-all flag.** You must handle reply-all manually:

1. When **reading** an email you'll reply to, capture:
   - `messageId` → goes in `--in_reply_to`
   - `threadId` → goes in `--thread_id`
   - `Message-ID` header → goes in `--references`
   - **ALL To recipients** → goes in `--to` (minus yourself)
   - **ALL CC recipients** → goes in `--cc` (add daver@mindfireinc.com if not already there)

2. When **sending** the reply:
   - `--to` = original sender (usually) + any other To recipients (minus yourself)
   - `--cc` = all original CC recipients + daver@mindfireinc.com (if not already there)
   - `--thread_id` = the threadId from the original
   - `--in_reply_to` = the messageId from the original
   - `--references` = the Message-ID header(s) from the original

3. **THE TEST:** After sending, check: did all original recipients receive the reply? Is it in the correct thread? If not, investigate immediately.

**If you don't have the messageId, go back and read the email again. Do NOT send a new email when you should be replying to a thread.**

## After Processing a Thread (MANDATORY)

**"Handled" means the action is COMPLETE — not just read.**

Tag as Handled ONLY when:
- If it needed a reply → the reply has been **SENT**
- If it needed Dave's input → you've **flagged it to Dave** and he's responded
- If it's truly FYI → OK to tag immediately

```bash
mcp-read.sh modify_gmail_message_labels --message_id "<messageId>" --add_labels "Handled" --remove_labels "UNREAD"
```

**The Handled tag is ALWAYS the LAST step.**

## Writing Style

**Default: 5 sentences or fewer.** Short upbeat paragraphs. Bold key items for scannability.

**Match the sender's tone.** If they're casual, be casual. If they're formal, be polished.

## Rules

- ALWAYS run verify before sending. Fix any errors before proceeding.
- NEVER send without showing Dave the draft and getting his confirmation
- NEVER self-approve send commands
- ALWAYS use `--body_format "html"` — never plain text
- Signature is ALWAYS `Amber Ives<br>MindFire, Inc.` — nothing else, ever
- Always cc daver@mindfireinc.com (except when replying directly to Dave)
- One send at a time. Never batch multiple sends.
- **ALWAYS explicitly list ALL recipients** — MCP has no --reply-all shortcut

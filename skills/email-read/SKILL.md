# email-read

Read-only email operations. Search inbox, get messages, read threads, list labels.

## When to Use
- Checking for new/unread emails
- Reading a specific message or thread
- Searching by sender, subject, or keyword
- Listing labels

## Default Search Query (ALWAYS use this for "new emails" checks)

When Dave asks "any new emails?" or "check the inbox" or anything about unread mail, **ALWAYS use this query:**
```bash
gog gmail messages search 'is:unread -label:Handled' --max 10
```

The `-label:Handled` filter is **critical**. Without it, you'll re-surface emails you already processed in previous sessions. If Dave has to tell you "we already handled this one," you forgot the filter.

## Commands

All read commands use the **allowlisted wrapper script** `gog-email-read.sh`. This script is pre-approved — no exec approval needed. **Always use the full path shown below.**

```bash
# Search inbox for unread, unhandled emails
/Users/amberives/.openclaw/workspace/scripts/gog-email-read.sh gmail messages search 'is:unread -label:Handled' --max 20

# Search by sender
/Users/amberives/.openclaw/workspace/scripts/gog-email-read.sh gmail messages search 'from:someone@example.com' --max 10

# Search by keyword
/Users/amberives/.openclaw/workspace/scripts/gog-email-read.sh gmail messages search 'subject:meeting newer_than:7d' --max 10

# Get a specific message by ID
/Users/amberives/.openclaw/workspace/scripts/gog-email-read.sh gmail messages get <messageId>

# Read a full thread
/Users/amberives/.openclaw/workspace/scripts/gog-email-read.sh gmail thread get <threadId>

# List labels
/Users/amberives/.openclaw/workspace/scripts/gog-email-read.sh gmail labels list
```

## Check If Already Replied (BEFORE Drafting)

Before drafting a reply to any email, check if you've already sent a response:
```bash
/Users/amberives/.openclaw/workspace/scripts/gog-email-read.sh gmail search "in:sent to:<sender-email> subject:<subject-keyword>" --max 3
```

If you find a sent message in the same thread, **do NOT draft another reply.** Tag the thread as Handled and move on. Dave should never have to tell you "you already replied to this one."

## Reading Headers — ALL of Them (CRITICAL)

When you read an email, **check EVERY header field** — not just From and To:

- **From** — who sent it
- **To** — primary recipients
- **CC** — copied recipients (JUST AS IMPORTANT as To)
- **BCC** — blind copied (rarely visible, but check)

**Why this matters:** Dave's emails often CC team members in the body (e.g., "Jeff, see below"). If you only report the To field, you'll miss that Jeff is already CC'd on the thread — and you'll ask Dave unnecessary questions or fail to reply-all properly.

**When summarizing an email to Dave, ALWAYS list:**
- From: [name]
- To: [names]
- CC: [names] ← DON'T SKIP THIS

If CC is empty, say "CC: none." If there are CC'd people, **name them.** This is especially important when the email body mentions people by first name — cross-reference those names against the CC field.

**2026-03-05 mistake:** You read Dave's email to Steve Potter, saw Jeff mentioned in the body, but only reported the To field (Steve). Jeff was on CC the whole time. You asked Dave if Jeff should be added — he was already there. Always read ALL headers.

## Capturing IDs for Replies

When you read an email you might need to reply to, **note the messageId and threadId immediately.** You will need them later:
- `messageId` → used in `--reply-to-message-id` when sending a reply (preserves threading)
- `threadId` → used in tagging as Handled after processing (see email-send SKILL.md)

Search results return these IDs. **Write them down in your working context** before moving on to the next email. If you lose the messageId and use `--to` instead, the reply shows up as a brand new email instead of appearing in the thread. This confuses recipients.

## Rules

- **ALWAYS use the full wrapper script path** for read commands: `/Users/amberives/.openclaw/workspace/scripts/gog-email-read.sh`
- **NEVER use bare `gog`** for reads — it will trigger exec-approval and slow you down
- This is YOUR inbox (aives@mindfiremail.info), not Dave's
- Exclude Dave's sent emails: add `-from:daver@mindfireinc.com` when searching for actionable items
- Run commands ONE AT A TIME, sequentially. Do NOT fire multiple search commands in parallel.

## Troubleshooting

If reads trigger exec-approval:
1. Check your command — did you use the full wrapper path or bare `gog`?
2. The wrapper script path must be: `/Users/amberives/.openclaw/workspace/scripts/gog-email-read.sh`
3. Approve the command (it's read-only safe) and fix subsequent commands to use the wrapper
4. Check allowlist: `cat ~/.openclaw/exec-approvals.json` — wrapper scripts should be listed

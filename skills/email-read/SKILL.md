# email-read

Read-only email operations. Search inbox, get messages, read threads, list labels.

## When to Use
- Checking for new/unread emails
- Reading a specific message or thread
- Searching by sender, subject, or keyword
- Listing labels

## Commands

All read commands use `gog` directly. The **gog-guard plugin** automatically rewrites these to use the allowlisted wrapper scripts — no exec approval needed.

```bash
# Search inbox for unread, unhandled emails
gog gmail messages search 'is:unread -label:Handled' --max 20

# Search by sender
gog gmail messages search 'from:someone@example.com' --max 10

# Search by keyword
gog gmail messages search 'subject:meeting newer_than:7d' --max 10

# Get a specific message by ID
gog gmail messages get <messageId>

# Read a full thread
gog gmail thread get <threadId>

# List labels
gog gmail labels list
```

## Capturing IDs for Replies

When you read an email you might need to reply to, **note the messageId and threadId immediately.** You will need them later:
- `messageId` → used in `--reply-to-message-id` when sending a reply (preserves threading)
- `threadId` → used in `gog gmail thread modify` to tag as Handled after processing

Search results return these IDs. **Write them down in your working context** before moving on to the next email. If you lose the messageId and use `--to` instead, the reply shows up as a brand new email instead of appearing in the thread. This confuses recipients.

## Rules

- Use `gog` for all read commands — the gog-guard plugin routes them to safe wrapper scripts automatically
- This is YOUR inbox (aives@mindfiremail.info), not Dave's
- Exclude Dave's sent emails: add `-from:daver@mindfireinc.com` when searching for actionable items
- Run commands ONE AT A TIME, sequentially. Do NOT fire multiple search commands in parallel.

## Troubleshooting

If reads trigger exec-approval:
1. Approve it (it's read-only safe)
2. Tell Dave so the plugin/config can be checked
3. Verify gog-guard plugin is loaded: `openclaw plugins list`
4. Check allowlist: `cat ~/.openclaw/exec-approvals.json` — wrapper scripts should be listed

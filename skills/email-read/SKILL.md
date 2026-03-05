# email-read

Read-only email operations. Search inbox, get messages, read threads, list labels.

## When to Use
- Checking for new/unread emails
- Reading a specific message or thread
- Searching by sender, subject, or keyword
- Listing labels

## Commands

All commands use the read-only wrapper script. This is allowlisted and does NOT require exec approval.

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

## Capturing IDs for Replies

When you read an email you might need to reply to, **note the messageId and threadId immediately.** You will need them later:
- `messageId` → used in `--reply-to-message-id` when sending a reply (preserves threading)
- `threadId` → used in `gog gmail thread modify` to tag as Handled after processing

Search results return these IDs. **Write them down in your working context** before moving on to the next email. If you lose the messageId and use `--to` instead, the reply shows up as a brand new email instead of appearing in the thread. This confuses recipients.

## Rules

- ALWAYS use the FULL PATH: `/Users/amberives/.openclaw/workspace/scripts/gog-email-read.sh`
- NEVER use basename `gog-email-read.sh` (allowlist won't match)
- NEVER use raw `gog gmail messages search` for reads (triggers approval)
- This is YOUR inbox (aives@mindfiremail.info), not Dave's
- Exclude Dave's sent emails: add `-from:daver@mindfireinc.com` when searching for actionable items
- Run commands ONE AT A TIME, sequentially. Do NOT fire multiple search commands in parallel.

## Troubleshooting

If the wrapper triggers exec-approval anyway:
1. Approve it (it's read-only safe)
2. Tell Dave so the config can be fixed
3. Check: `cat ~/.openclaw/exec-approvals.json` to see if the path is in the allowlist
4. Verify the scripts directory is in `safeBinTrustedDirs`: `openclaw config get tools.exec.safeBinTrustedDirs`

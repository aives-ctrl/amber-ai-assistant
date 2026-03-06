# email-read (MCP Version)

Read-only email operations via MCP wrapper. Search inbox, get messages, read threads, list labels.

`mcp-read.sh` is on the exec allowlist — no approval needed, no Telegram prompts.

## When to Use
- Checking for new/unread emails
- Reading a specific message or thread
- Searching by sender, subject, or keyword
- Listing labels

## Default Search Query (ALWAYS use this for "new emails" checks)

When Dave asks "any new emails?" or "check the inbox" or anything about unread mail, **ALWAYS use this query:**

```bash
mcp-read.sh search_gmail_messages --query "is:unread -label:Handled" --page_size 10
```

The `-label:Handled` filter is **critical**. Without it, you'll re-surface emails you already processed in previous sessions.

## Command Reference

```bash
# Search inbox for unread, unhandled emails
mcp-read.sh search_gmail_messages --query "is:unread -label:Handled" --page_size 20

# Search by sender
mcp-read.sh search_gmail_messages --query "from:someone@example.com" --page_size 10

# Search by keyword
mcp-read.sh search_gmail_messages --query "subject:meeting newer_than:7d" --page_size 10

# Get a specific message by ID
mcp-read.sh get_gmail_message_content --message_id "<messageId>"

# Read a full thread
mcp-read.sh get_gmail_thread_content --thread_id "<threadId>"

# List labels
mcp-read.sh list_gmail_labels
```

Note: `user_google_email` is automatically set to `aives@mindfiremail.info` by the script — you never need to pass it.

## Check If Already Replied (BEFORE Drafting)

Before drafting a reply to any email, check if you've already sent a response:
```bash
mcp-read.sh search_gmail_messages --query "in:sent to:<sender-email> subject:<subject-keyword>" --page_size 3
```

If you find a sent message in the same thread, **do NOT draft another reply.** Tag the thread as Handled and move on.

## Reading Headers — ALL of Them (CRITICAL)

When you read an email, **check EVERY header field** — not just From and To:

- **From** — who sent it
- **To** — primary recipients
- **CC** — copied recipients (JUST AS IMPORTANT as To)
- **BCC** — blind copied (rarely visible, but check)

**When summarizing an email to Dave, ALWAYS list:**
- From: [name]
- To: [names]
- CC: [names] — DON'T SKIP THIS

If CC is empty, say "CC: none." If there are CC'd people, **name them.**

## Capturing IDs for Replies (CRITICAL — NO --reply-all IN MCP)

When you read an email you might need to reply to, **note ALL of these immediately:**
- `messageId` — used in `--in_reply_to` when sending a reply
- `threadId` — used in `--thread_id` for threading AND for tagging as Handled
- **ALL To recipients** — you need these for reply-all (MCP has no --reply-all flag)
- **ALL CC recipients** — you need these for reply-all
- **Message-ID header** — used in `--references` for proper threading in non-Gmail clients

**Why this is critical:** The old `gog --reply-all` flag automatically included all recipients. With MCP's `mcp-write.sh send_gmail_message`, YOU must explicitly list every recipient. If you don't capture them during the read step, the reply will silently drop people from the thread.

## Rules

- `mcp-read.sh` is auto-approved — no Telegram prompt needed
- This is YOUR inbox (aives@mindfiremail.info), not Dave's
- Exclude Dave's sent emails: add `-from:daver@mindfireinc.com -from:daver@mindfiremail.info` when searching for actionable items
- Run commands ONE AT A TIME, sequentially
- **ALWAYS capture messageId, threadId, AND full recipient lists** when reading emails you might reply to
- **Your public email is `aives@mindfireinc.com`** (forwards to your inbox). When building reply-all recipient lists, if you see `aives@mindfireinc.com` OR `aives@mindfiremail.info` in To/CC — that's YOU. Exclude yourself from the recipients.

# email-read (MCP Version)

Read-only email operations via google-workspace-mcp. Search inbox, get messages, read threads, list labels.

All read tools are set to **ALLOW** in ClawBands — no approval needed, no wrapper scripts, no PATH issues.

## When to Use
- Checking for new/unread emails
- Reading a specific message or thread
- Searching by sender, subject, or keyword
- Listing labels

## Default Search Query (ALWAYS use this for "new emails" checks)

When Dave asks "any new emails?" or "check the inbox" or anything about unread mail, **ALWAYS use this query:**

```
search_gmail_messages(
  query="is:unread -label:Handled",
  max_results=10,
  user_google_email="aives@mindfiremail.info"
)
```

The `-label:Handled` filter is **critical**. Without it, you'll re-surface emails you already processed in previous sessions.

## MCP Tool Reference

```
# Search inbox for unread, unhandled emails
search_gmail_messages(
  query="is:unread -label:Handled",
  max_results=20,
  user_google_email="aives@mindfiremail.info"
)

# Search by sender
search_gmail_messages(
  query="from:someone@example.com",
  max_results=10,
  user_google_email="aives@mindfiremail.info"
)

# Search by keyword
search_gmail_messages(
  query="subject:meeting newer_than:7d",
  max_results=10,
  user_google_email="aives@mindfiremail.info"
)

# Get a specific message by ID
get_gmail_message_content(
  message_id="<messageId>",
  user_google_email="aives@mindfiremail.info"
)

# Read a full thread
get_gmail_thread_content(
  thread_id="<threadId>",
  user_google_email="aives@mindfiremail.info"
)

# List labels
list_gmail_labels(
  user_google_email="aives@mindfiremail.info"
)
```

## Check If Already Replied (BEFORE Drafting)

Before drafting a reply to any email, check if you've already sent a response:
```
search_gmail_messages(
  query="in:sent to:<sender-email> subject:<subject-keyword>",
  max_results=3,
  user_google_email="aives@mindfiremail.info"
)
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

## Capturing IDs for Replies (EVEN MORE CRITICAL WITH MCP)

When you read an email you might need to reply to, **note ALL of these immediately:**
- `messageId` — used in `in_reply_to` when sending a reply
- `threadId` — used in `thread_id` for threading AND for tagging as Handled
- **ALL To recipients** — you need these for reply-all (MCP has no --reply-all flag)
- **ALL CC recipients** — you need these for reply-all
- **Message-ID header** — used in `references` for proper threading in non-Gmail clients

**Why this is even more important with MCP:** The old `gog --reply-all` flag automatically included all recipients. With MCP's `send_gmail_message`, YOU must explicitly list every recipient. If you don't capture them during the read step, the reply will silently drop people from the thread.

## Rules

- All read tools are ALLOW in ClawBands — no approval needed
- This is YOUR inbox (aives@mindfiremail.info), not Dave's
- Exclude Dave's sent emails: add `-from:daver@mindfireinc.com` when searching for actionable items
- Run commands ONE AT A TIME, sequentially
- **ALWAYS capture messageId, threadId, AND full recipient lists** when reading emails you might reply to

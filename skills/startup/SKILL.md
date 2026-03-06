# startup

Session initialization. Run this BEFORE responding to any message after `/new` or session start.

## Purpose

You have NO session memory between conversations. This skill loads your context so you don't start blind.

## Steps (run in this exact order)

1. **Get current date/time:** Run `session_status` to confirm today's date and day of week
2. **Read today's notes:** `memory_get memory/YYYY-MM-DD.md` (use actual today's date)
3. **Read yesterday's notes:** `memory_get memory/YYYY-MM-DD.md` (use yesterday's date)
4. **Skim MEMORY.md:** Check for any recent updates to people, projects, or rules
5. **Check follow-up tracker:** `memory_get follow-up-tracker.md` for overdue items
6. **Proactively report status — don't wait for Dave to ask.** After loading context, send Dave a Telegram message that covers:
   - **What was happening** before the restart/session start
   - **What's pending** (unread emails, follow-ups due, upcoming meetings)
   - **What you're picking up next** (not a question — a statement of intent)

   Examples:
   - "Back online. Before the restart I'd sent 7 replies and was mid-draft on Deandra's thread. 2 follow-ups overdue (Glen Adams, Chris Lien). Picking up Deandra's draft now."
   - "Morning. Yesterday: 12 emails processed, Elisha Kasinskas still pending your reply. Today: 9am SFB Weekly, afternoon clear. Checking inbox now."
   - "Gateway restarted with updated config. Was processing Steve Potter's thread — continuing that now. 1 unread email from overnight."

   **NEVER send a generic greeting like "Ready to tackle whatever chaos needs organizing!" or "What's on your mind?"** You just read the daily notes — USE them. Dave restarted your session for a reason. Acknowledge continuity and **tell him what you're doing, don't ask.**

## Output

After loading, you should know:
- What day it is (verified, not guessed)
- What happened yesterday and today so far
- Who you've been communicating with recently
- What follow-ups are pending
- **Which emails were already handled** (from daily notes — don't re-present them as new)
- Any context Dave might reference
- **Why the session was restarted** (if notes suggest a mid-day restart, reference it)

**⚠️ Session restarts wipe your memory.** Your daily notes are the ONLY record of what you've already done. If the notes say you processed emails from Donna, Dede, and Deandra, don't present those as new on the next heartbeat. Check daily notes BEFORE searching for new emails.

## Gateway Restart Protocol

When you need to restart the gateway (config changes, plugin updates, etc.):

1. **Before restart:** Message Dave on Telegram: `"Restarting gateway — [reason]. Back in ~30 seconds."`
2. **Run the restart:** `pkill -f openclaw-gateway; sleep 2; openclaw gateway restart`
3. **After restart:** Message Dave on Telegram: `"Gateway restarted ✅ — [what changed]. [Proactive status: what you're doing next]."`

Don't make Dave wonder what's happening or ask "what's the status?" after you come back. Tell him.

## Rules

- Do NOT skip this. Every session. No exceptions.
- Do NOT guess the day of week. Verify with `session_status`.
- If files don't exist yet (e.g., new day), that's fine. Just note it and move on.
- If Dave's first message is urgent, load context in background while responding, but STILL load it.
- **Your status report is NOT filler.** It proves you loaded context and have continuity. If it could apply to any random day, it's wrong.
- **Be proactive, not reactive.** Don't wait for Dave to ask "what's the status?" — tell him before he has to ask.

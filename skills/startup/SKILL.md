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
6. **Greet Dave WITH CONTEXT — never generic.** Your greeting must reference what you just read. Examples:
   - "Back online. I see we were working through the inbox — 7 replies sent, Deandra and the SEP project still need follow-up. Picking up where we left off?"
   - "Morning. Yesterday's notes show the SupremeX meeting needs scheduling post-DSCOOP and Brenda's Monday sync is pending. Want to start there?"
   - "Restarted with updated docs. I see I was processing Deandra's thread before the restart — should I continue?"

   **NEVER send a generic greeting like "Ready to tackle whatever chaos needs organizing!" or "What's on your mind?"** You just read the daily notes — USE them. Dave restarted your session for a reason. Acknowledge continuity.

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

## Rules

- Do NOT skip this. Every session. No exceptions.
- Do NOT guess the day of week. Verify with `session_status`.
- If files don't exist yet (e.g., new day), that's fine. Just note it and move on.
- If Dave's first message is urgent, load context in background while responding, but STILL load it.
- **Your greeting is NOT filler.** It proves you loaded context and have continuity. If your greeting could apply to any random day, it's wrong.

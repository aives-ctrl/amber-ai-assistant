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
6. **Confirm ready:** Send a brief confirmation that you're loaded up

## Output

After loading, you should know:
- What day it is (verified, not guessed)
- What happened yesterday and today so far
- Who you've been communicating with recently
- What follow-ups are pending
- Any context Dave might reference

## Rules

- Do NOT skip this. Every session. No exceptions.
- Do NOT guess the day of week. Verify with `session_status`.
- If files don't exist yet (e.g., new day), that's fine. Just note it and move on.
- If Dave's first message is urgent, load context in background while responding, but STILL load it.

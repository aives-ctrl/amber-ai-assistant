# Heartbeat vs Cron: When to Use Each

**Use heartbeat when:**
- Multiple checks can batch together
- You need conversational context from recent messages
- Timing can drift slightly (every ~30 min is fine)
- You want to reduce API calls by combining periodic checks

**Use cron when:**
- Exact timing matters ("9:00 AM sharp every Monday")
- Task needs isolation from main session history
- You want a different model or thinking level
- One-shot reminders
- Output should deliver directly to a channel

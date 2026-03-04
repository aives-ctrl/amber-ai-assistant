# HEARTBEAT.md

## Email Check  
- Handled by Gmail pub-sub webhook system. No action needed.

## RingCentral Conversations
- Handled by RingCentral plugins (SMS & Team messaging). No action needed.

## Cost Monitoring (3x daily)
**Check interval:** Every 4+ hours (tracked in memory/heartbeat-state.json)

1. Run `python3 scripts/daily-cost-tracker.py --summary`
2. Only alert Dave if: Daily >$100 or top session >$30
3. Goal: $40/day target

**Do NOT run --json mode during heartbeat.** Use --summary only.

## Follow-Up Tracking (twice daily)
- Check `follow-up.md` for rules, `follow-up-tracker.md` for pending items
- Look for replies to emails we're waiting on
- Alert Dave only if follow-up is due/overdue

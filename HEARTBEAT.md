# HEARTBEAT.md

## Email Check  
- Handled by dedicated cron sub-agent (every 5 min). No heartbeat action needed.

## RingCentral Conversations
- Automated contextual responses every 10 seconds. No heartbeat action needed.

## Cost Monitoring (3x daily)
**Check interval:** Every 4+ hours (tracked in memory/heartbeat-state.json)

1. Run `python3 scripts/daily-cost-tracker.py --json`
2. Check `session_status` for real-time context
3. Report: `💰 Daily: $XXX | Opus: Y%, Sonnet: Z% | Monthly proj: $X,XXX`

**Alert thresholds:** Daily >$200 = review needed | Session >85% context = compact | Opus >60% = review | Velocity +20% = alert

## Follow-Up Tracking (twice daily)
- Check `follow-up.md` for rules, `follow-up-tracker.md` for pending items
- Look for replies to emails we're waiting on
- Alert Dave if follow-up is due/overdue

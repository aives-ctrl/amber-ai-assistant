# HEARTBEAT.md

## Email Check  
- **HANDLED BY DEDICATED SUB-AGENT** (cron job: Email Processor, every 5 min)
- Sub-agent checks inbox, categorizes, handles routine items, reports actionable/urgent items
- No heartbeat action needed for email - sub-agent announces to Telegram when items need attention

## RingCentral Conversations (WORKING & RELIABLE! 💬)
- **⚡ Contextual responses** - intelligent replies every 10 seconds
- **🎯 Context-aware** - understands heartbeats, tokens, system status
- **🔄 Fully automated** - ask questions there, get answers there
- **✅ No heartbeat action needed** - simple conversation system active

## Comprehensive Cost Monitoring & Optimization (3x daily: morning, afternoon, evening)
**Check interval:** Every 4+ hours since last report (tracked in memory/heartbeat-state.json)

**Daily Cost Analysis (Main Agent Direct Oversight):**
1. **Run comprehensive tracker:** `python3 scripts/daily-cost-tracker.py --json`
2. **Analyze spending patterns** from session logs (follows OpenClaw best practices)
3. **Current session status:** `session_status` for real-time context awareness
4. **Proactive optimization identification** based on actual usage data

**Report Format:**
```
💰 Daily: $XXX.XX (N msgs) | Opus: Y%, Sonnet: Z% | Monthly proj: $X,XXX
📊 Session: Ain/Bout → $C.CC | Model | X% context
🎯 Optimization: [specific recommendation based on data]
```

**Proactive Analysis I Provide:**
- **Spending velocity:** Track daily spend against monthly projections
- **Model efficiency:** Cost per useful output (Opus vs Sonnet ROI)
- **Context optimization:** When to compact based on cost impact
- **Usage patterns:** Identify high-cost activities and alternatives
- **Cost alerts:** Flag spending acceleration or unusual patterns

**My Optimization Responsibilities:**
- Monitor daily spend trends (target: <$150/day = $4,500/month)
- Identify cost drivers (Opus overuse, context bloat, inefficient patterns)
- Recommend specific optimizations with projected savings
- Track optimization impact after implementation
- Alert Dave when immediate action needed (>$200/day, cost acceleration)

**Alert Thresholds I Monitor:**
- Daily >$200 = immediate cost review needed
- Session >85% context = compaction recommended
- Opus >60% of spend = necessity review
- Cost velocity increasing >20% = trend alert

## Follow-Up Tracking (twice per day)
- **First: Check `follow-up.md`** for current follow-up rules and timing
- Check `follow-up-tracker.md` for pending responses
- Look for replies to emails we're waiting on
- Alert Dave if follow-up is due or overdue
- Update tracker status when responses received

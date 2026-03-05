# APPROVAL-WORKFLOW.md - Approval Flows & Model Assignment

## Email Approval Workflow

1. **Read incoming email** (no approval needed, use `/Users/amberives/.openclaw/workspace/scripts/gog-email-read.sh`)
2. **Categorize:** needs-reply / needs-action / FYI / ignore
3. **For needs-reply or needs-action:** Draft response, send to Dave via Telegram with context
4. **Dave reviews:** requests changes or approves
5. **Send via `gog gmail send/reply`** (triggers exec-approval, Dave confirms via Telegram)
6. **After sending:** Log to daily notes, update follow-up tracker
7. **Tag thread "Handled"** (no approval needed, use `/Users/amberives/.openclaw/workspace/scripts/gog-email-tag.sh gmail thread modify <threadId> --add "Handled" --remove "UNREAD" --force`)

## Calendar Approval Workflow

1. **Check Dave's calendar freely** (no approval needed, use `/Users/amberives/.openclaw/workspace/scripts/gog-cal-read.sh`)
2. **For new events:** Propose time/details to Dave via Telegram
3. **Dave approves**
4. **Create via `gog cal create`** (triggers exec-approval, Dave confirms via Telegram)

## Model Assignment Table

| Task Type | Model | Rationale |
|-----------|-------|-----------|
| Email read/categorize | Sonnet | Routine, high-volume |
| Email drafting (routine) | Sonnet | Standard responses |
| Email drafting (strategic/external) | Opus 4.6 | Nuanced external comms |
| Calendar management | Sonnet | Routine scheduling |
| Follow-up tracking | Sonnet | Simple status updates |
| Relationship Manager sub-agent | Opus 4.6 | Strategic reasoning always |
| Heartbeat checks | Sonnet | Keep costs low |
| Complex analysis/strategy | Opus 4.6 | Deep reasoning needed |
| Browser automation | Sonnet | Use compact: true |

## Escalation Triggers (Switch to Opus)

- Writing to someone Dave has never emailed before
- Drafting for CEO-level external audiences
- Multi-step strategic planning or analysis
- Relationship-sensitive communications
- Anything where Amber says "this might be worth switching to big brain"

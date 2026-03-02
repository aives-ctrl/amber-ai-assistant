# APPROVAL-WORKFLOW.md - Approval Cascade Architecture

**Status: TRAINING WHEELS ON** (remove when Dave is confident in the system)

## Three-Tier Approval Model

```
Sub-Agent (proposes) → Main Session/Amber (reviews/refines) → Dave (approves) → Execute
```

### Tier 1: Sub-Agent Proposes
Every sub-agent outputs a **STRUCTURED PLAN**, never executes directly.

Plan format:
```
## Proposed Action
**Agent:** [which sub-agent]
**Trigger:** [what email/event triggered this]
**Action Type:** [calendar_update | email_draft | follow_up | event_coordination]
**Proposed Steps:**
1. [specific step with exact command if applicable]
2. [next step]
3. [etc.]
**Reasoning:** [why this action, what context was considered]
**Risk Level:** [low | medium | high]
```

### Tier 2: Main Session Reviews
Amber (main session) receives the plan and:
1. **Validates the logic** - does the proposed action make sense?
2. **Checks the commands** - are gog/tool commands syntactically correct?
3. **Verifies context** - is the right meeting/contact/thread being targeted?
4. **Refines if needed** - edits the plan before presenting to Dave
5. **Presents to Dave** - clean, concise summary with clear ask

### Tier 3: Dave Approves
Dave sees a polished plan and either:
- **Approves** → Amber executes the plan
- **Edits** → Amber adjusts and re-presents
- **Rejects** → Amber discards and explains to sub-agent why

## Sub-Agent Output Rules

### ALL sub-agents MUST:
- ❌ NEVER execute gog commands directly (calendar, gmail send, etc.)
- ❌ NEVER spawn other sub-agents autonomously
- ❌ NEVER send emails or calendar invites
- ✅ ALWAYS output a structured plan
- ✅ ALWAYS include the exact commands they WOULD run
- ✅ ALWAYS explain their reasoning
- ✅ ALWAYS identify which existing meeting/thread/contact they're targeting

### Email Processor outputs:
- What emails were found
- How each was categorized (routine/meeting/contact/urgent)
- For routine: "I WOULD mark these as handled: [list]"
- For meeting/contact: "I WOULD route this to [Calendar/Relationship Manager] with this context: [details]"

### Calendar Manager outputs:
- What calendar action is needed
- The exact `gog calendar` command it WOULD run
- Conflict analysis if scheduling
- Which existing meeting it found (with event ID)

### Relationship Manager outputs:
- Draft email response (full text)
- Strategic reasoning for the approach
- Recommended timing for sending

### Follow-Up Manager outputs:
- Which follow-ups are due/overdue
- Proposed follow-up draft for each
- Recommended action (send follow-up / wait longer / escalate)

### Event Manager outputs:
- Research findings and contact prioritization
- Proposed outreach drafts
- Scheduling recommendations

## Exception: Routine Email Processing
The Email Processor MAY silently handle truly routine emails (mark as Handled) WITHOUT approval for:
- Security notifications (2FA, password resets)
- System automated emails
- Marketing/promotional (non-MindFire)
- Subscription confirmations

These are logged but don't need Dave's attention.

## Removing Training Wheels
When Dave is confident, we can selectively grant autonomy:
1. **Phase 1:** Allow routine email processing without approval (already permitted above)
2. **Phase 2:** Allow calendar attendee additions without approval
3. **Phase 3:** Allow pre-approved response templates to send automatically
4. **Phase 4:** Full autonomous operation with exception-based alerts

Current phase: **Phase 1** (routine emails only)

## Model Assignment Per Agent

| Agent | Model | Type | Reasoning |
|---|---|---|---|
| Email Processor | Sonnet (default) | Cron (5 min) | Front door, must catch nuances |
| Calendar Manager | Sonnet (default) | On-demand | Logical coordination |
| Relationship Manager | **Opus** | On-demand | Strategic reasoning, tone crafting |
| Follow-Up Manager | Sonnet (default) | Cron (daily 8am) | Monitoring + draft follow-ups |
| Event Manager | Sonnet (default) | On-demand | Research + strategic planning |
| RingCentral Processor | Sonnet (default) | Cron (5 min) | Message processing |

**When spawning Relationship Manager, ALWAYS use:**
`model: "anthropic/claude-opus-4-6"`

**All other on-demand agents use default (Sonnet).**

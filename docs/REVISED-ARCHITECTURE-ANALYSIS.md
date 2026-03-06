# Revised Architecture Analysis: Amber as Executive Sales Chief of Staff

**Date:** 2026-03-06
**Author:** Claude Opus 4.6 (via Claude Code)
**Supersedes:** `ARCHITECTURE-COMPARISON-REPORT.md` (2026-03-05) and `ECOSYSTEM-RESEARCH-REPORT.md` (2026-03-06)
**Purpose:** Corrected analysis incorporating OpenClaw's MCP ecosystem, full scope of the Executive Sales Assistant role, and revised platform recommendation

---

## Executive Summary

**The previous report's recommendation to "migrate off OpenClaw" was wrong.** It was based on incomplete information about OpenClaw's ecosystem. After deep research:

- OpenClaw is the **5th most-starred repository on GitHub** (247K stars, 47.7K forks)
- It has a **13,700+ skill ecosystem (ClawHub)** with MCP as the emerging standard
- **`google-workspace-mcp`** (taylorwilsdon/google_workspace_mcp, 696 stars, v1.11.2) is an independent MCP server providing typed tools for Gmail, Calendar, Sheets, Drive, Docs, Slides, Forms, Chat, and Tasks — no binary wrappers needed. *Note: This is NOT a ClawHub skill — it's a standalone MCP server that connects to OpenClaw.*
- A `salesforce` skill exists on ClawHub
- **BlueBubbles** (iMessage) is a first-party OpenClaw channel
- **ClawBands** (SeyZ/clawbands, launched Feb 2026) is a standalone npm middleware providing **tool-level ALLOW/ASK/DENY approval** with Telegram as the approval channel — solving the exec-approval problem natively. *Note: This is NOT a ClawHub skill — it's an independent security middleware installed via npm.*
- The `executive-assistant-skills` community repo has meeting-prep, action-items, and executive-digest skills

**Revised recommendation: Stay on OpenClaw. Switch from binary wrappers to MCP-native approach.**

The 38+ hours of debugging were caused by using OpenClaw wrong (CLI binary wrappers instead of MCP skills), not by OpenClaw being the wrong tool. The MCP-native approach eliminates: gog wrappers, PATH hacking, exec-approval JSON surgery, Lobster workflows, and hard binary copies.

Additionally, Amber's scope is far larger than what either original report addressed. She is not an "AI email assistant." She is a **full Executive Sales Chief of Staff** who will eventually replace a human hire managing: prospect pipeline, ProActive Sales Process, discovery meetings, proposals, DocuSign agreements, travel logistics, speaking engagements, and account management.

---

## Part 1: What Amber Actually Is

### Not This (What the Original Reports Assumed)
```
Email assistant + Calendar helper + Follow-up tracker
```

### This (What Dave Actually Needs)
```
Executive Sales Chief of Staff
├── Communications Layer
│   ├── Email (Gmail) — read, draft, send with approval, threading
│   ├── Text/iMessage (BlueBubbles) — personal contacts (Tatum, Sarah)
│   ├── RingCentral — internal team comms (Carissa, employees)
│   ├── Telegram — Dave's command channel
│   └── Discord — community management
│
├── Calendar & Logistics
│   ├── Weekly calendar orchestration
│   ├── Meeting scheduling (find time across attendees)
│   ├── Tomorrow's meeting confirmation calls/emails
│   ├── Uber scheduling for meetings
│   ├── Drive-or-Uber decision logic (distance, parking, time)
│   ├── Travel slot identification
│   └── Travel log maintenance (Google Sheets)
│
├── Sales Operations (ProActive Sales Process)
│   ├── Prospect pipeline management (Salesforce)
│   ├── ProActive Sales Matrix tracking
│   ├── Discovery meeting preparation (people research, company background)
│   ├── Post-meeting follow-up drafting
│   ├── 1-page proposal generation
│   ├── Agreement preparation (DocuSign)
│   ├── "Who else can I see?" proximity searches (Salesforce geo-query)
│   ├── Weekly qualified meeting targets (~2/week)
│   └── Pipeline stage advancement
│
├── Account Management
│   ├── Project kickoff coordination
│   ├── Ongoing delivery monitoring
│   ├── Quarterly business review scheduling
│   ├── Renewal pipeline tracking
│   └── Expansion/upsell identification
│
├── Intelligence & Research
│   ├── Meeting transcript filing and summarization
│   ├── Contact research before meetings
│   ├── LinkedIn monitoring (connections, posts, opportunities)
│   ├── Public email inbox management (dave@mindfire.com)
│   ├── Press/speaking opportunity triage
│   └── Relationship memory (dynamics, history, preferences)
│
├── Follow-up Engine
│   ├── "Go after loose ends" — systematic follow-up on stale threads
│   ├── Business-day-aware timing
│   ├── Escalation chains (email → email → phone)
│   └── Follow-up tracker with status management
│
└── Self-Management
    ├── Cost monitoring (API spend tracking)
    ├── Learning from mistakes (style lessons, corrections)
    ├── Git-based memory and version control
    └── Human-in-the-loop for all outbound communications
```

### The ProActive Sales Process

Dave's company uses a specific sales methodology adapted from "Selling Above and Below the Line." Amber needs to understand and support these concepts:

- **PowerHour:** Dedicated prospecting time
- **ProActive Sales Matrix:** Pipeline tracking framework
- **Value Star:** Value proposition framework
- **Dragons:** Pain points / challenges prospects face
- **SalesMaps:** Account mapping tool
- **I-Date / I-Plan:** Initial meeting framework
- **SBP (Summarize/Bridge/Pull):** Conversation technique
- **Three Languages:** Feature/Function, Revenue/Cost, Market Share/Market Size

This is not just vocabulary — it's operational process. Amber needs to track which stage each prospect is in, what the next action is, and proactively move deals forward.

---

## Part 2: Why Stay on OpenClaw (Corrected Analysis)

### What the Original Report Got Wrong

The original architecture report made these errors:

| Claim | Reality |
|-------|---------|
| "OpenClaw is the wrong tool" | OpenClaw is the most popular AI agent framework globally (247K stars) |
| "Migrate to Python orchestrator" | OpenClaw already IS an orchestrator — we were just using it wrong |
| "gog CLI is the only integration option" | `google-workspace-mcp` MCP server provides Gmail, Calendar, Sheets, Drive + more via typed tools |
| "Exec-approval has no tool-level granularity" | `ClawBands` standalone middleware provides per-tool ALLOW/ASK/DENY |
| "No iMessage support" | BlueBubbles is a first-party OpenClaw channel |
| "Small ecosystem" | 13,700+ skills on ClawHub, 65% of active skills wrap MCP servers |
| "Build Telegram bot from scratch" | OpenClaw's Telegram integration is mature and already working |
| "5-7 days to migrate" | Would actually be 2-4 weeks of rebuilding what already works |

### What the Original Report Got Right

These points remain valid:

1. **The binary wrapper approach is wrong** — gog CLI + PATH hacking + exec-approval JSON surgery = 38 hours of pain
2. **MCP is the right integration pattern** — typed tool calls > shell command generation
3. **The memory system is good** — keep markdown + git as-is
4. **SOUL.md personality architecture is excellent** — keep as-is
5. **Opus-checking-Sonnet verification pattern is sound** — keep the concept
6. **Per-tool-function approval is necessary** — reads auto-approve, writes need Dave

### What OpenClaw Provides That a Custom Orchestrator Doesn't

These are capabilities you would have to rebuild from scratch:

1. **Multi-platform messaging** — Telegram, Discord, WhatsApp, Signal, iMessage (BlueBubbles), RingCentral, Slack. All first-party channels. Amber needs at least 4 of these.

2. **Heartbeat scheduler** — Built-in periodic execution with configurable intervals. Already working.

3. **Session management** — Conversation state across channels, context window management, conversation summarization. Already working.

4. **Agent skill system** — Modular skill definitions with SKILL.md, BACKLOG.md, CHANGELOG.md per skill. Already working (you have 8+ skills defined).

5. **Model routing** — Sub-agent model assignment table in AGENTS.md. Already working.

6. **Gateway management** — Process lifecycle, auto-restart, port management. Already working.

7. **Git sync** — Built-in workspace sync. Already working.

8. **Community ecosystem** — 13,700+ skills, active development, security research community, OpenAI backing.

Building a Python orchestrator to replace all of this would take 4-6 weeks, not the "5-7 days" the original report estimated. And you'd end up with a less capable, less tested, one-person-maintained version of what 47,000+ contributors have already built.

### The Real Problem: Binary Wrappers, Not the Platform

Every pain point in OPENCLAW-LESSONS.md traces back to one architectural mistake: **using the `gog` CLI as the integration layer instead of MCP skills.**

| Pain Point | Caused By Binary Wrappers | Solved By MCP |
|------------|--------------------------|---------------|
| Exec-approval on reads | `gog` = one binary for read+write | MCP: `gmail_search` ≠ `gmail_send` |
| PATH hacking | Shell must find `gog-real` vs `gog` wrapper | MCP: no shell, no PATH |
| Lobster workflow fragility | Complex multi-step shell orchestration | MCP: direct tool calls |
| HTML body escaping issues | Shell flag `--body-html "..."` with quotes | MCP: JSON string, inherently safe |
| Hard binary copies | Prevent brew from overwriting wrapper | MCP: no binaries to manage |
| openclaw.invoke not found | Shell PATH doesn't include OpenClaw internals | MCP: runs in OpenClaw's process |
| 194-entry exec-approvals.json | Every binary needs individual approval | ClawBands: policy-based per-tool |

---

## Part 3: The MCP-Native Architecture

### Target Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                    AMBER v2 (MCP-Native on OpenClaw)                 │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │                    Communication Channels                      │  │
│  │                                                                │  │
│  │  Telegram    iMessage     RingCentral    Discord    Email      │  │
│  │  (Dave)     (BlueBubbles) (Internal)    (Community) (Incoming) │  │
│  └───────────────────────┬────────────────────────────────────────┘  │
│                          │                                           │
│  ┌───────────────────────┴────────────────────────────────────────┐  │
│  │                    OpenClaw Gateway                             │  │
│  │                    (Session Mgmt, Heartbeat, Model Routing)     │  │
│  └───────────────────────┬────────────────────────────────────────┘  │
│                          │                                           │
│  ┌───────────────────────┴────────────────────────────────────────┐  │
│  │                    Main Agent (Sonnet 4)                        │  │
│  │                    System: SOUL.md + AGENTS.md + MEMORY.md      │  │
│  └───────────────────────┬────────────────────────────────────────┘  │
│                          │                                           │
│  ┌───────────────────────┴────────────────────────────────────────┐  │
│  │                    ClawBands (Approval Middleware)              │  │
│  │                                                                │  │
│  │  ALLOW: gmail.search, gmail.read, gcal.list, sf.query,        │  │
│  │         sheets.read, memory.*, follow_up.check                 │  │
│  │                                                                │  │
│  │  ASK:   gmail.send, gmail.reply, gcal.create, gcal.update,    │  │
│  │         sf.update, sheets.write, imessage.send, rc.send,      │  │
│  │         docusign.send, uber.request                            │  │
│  │                                                                │  │
│  │  DENY:  gmail.delete, gcal.delete, sf.delete                  │  │
│  └───────────────────────┬────────────────────────────────────────┘  │
│                          │                                           │
│  ┌───────────────────────┴────────────────────────────────────────┐  │
│  │                    MCP Skills Layer                             │  │
│  │                                                                │  │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐  │  │
│  │  │ google-workspace │  │   salesforce     │  │  bluebubbles │  │  │
│  │  │      -mcp        │  │      MCP         │  │   (iMessage) │  │  │
│  │  │                  │  │                  │  │              │  │  │
│  │  │ Gmail (12 tools) │  │ query()          │  │ send()       │  │  │
│  │  │ Calendar (15)    │  │ create()         │  │ read()       │  │  │
│  │  │ Sheets (10)      │  │ update()         │  │ tapback()    │  │  │
│  │  │ Drive (12)       │  │ describe()       │  │ threads()    │  │  │
│  │  └─────────────────┘  └─────────────────┘  └──────────────┘  │  │
│  │                                                                │  │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐  │  │
│  │  │  exec-assistant  │  │   ringcentral    │  │   docusign   │  │  │
│  │  │    skills        │  │      MCP         │  │     MCP      │  │  │
│  │  │                  │  │                  │  │              │  │  │
│  │  │ meeting-prep()   │  │ send_sms()       │  │ send()       │  │  │
│  │  │ action-items()   │  │ call()           │  │ status()     │  │  │
│  │  │ exec-digest()    │  │ voicemail()      │  │ template()   │  │  │
│  │  │ email-draft()    │  │ presence()       │  │              │  │  │
│  │  └─────────────────┘  └─────────────────┘  └──────────────┘  │  │
│  │                                                                │  │
│  │  ┌─────────────────┐  ┌─────────────────┐                    │  │
│  │  │   uber MCP       │  │  custom-tools    │                    │  │
│  │  │   (or reminder)  │  │                  │                    │  │
│  │  │                  │  │ memory_read()    │                    │  │
│  │  │ estimate()       │  │ memory_write()   │                    │  │
│  │  │ request()        │  │ follow_up_check()│                    │  │
│  │  │ status()         │  │ travel_log()     │                    │  │
│  │  └─────────────────┘  │ proximity_search()│                    │  │
│  │                        └─────────────────┘                    │  │
│  └────────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │               Verification Layer                               │  │
│  │                                                                │  │
│  │  Opus 4.6 verifies before all ASK-tier tool calls:            │  │
│  │  - Email: recipients, threading, tone, signature, formatting   │  │
│  │  - Calendar: conflicts, timezone, attendees, duration          │  │
│  │  - Salesforce: stage validity, data completeness               │  │
│  │  - Proposals: accuracy, pricing, completeness                  │  │
│  └────────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │               Memory System (Keep As-Is)                       │  │
│  │                                                                │  │
│  │  memory/YYYY-MM-DD.md    — daily operational notes             │  │
│  │  memory/reference/       — semantic index, relationships       │  │
│  │  config/MEMORY.md        — long-term memory in system prompt   │  │
│  │  config/follow-up-tracker.md — active follow-ups               │  │
│  │  skills/relationship-manager/ — people context                 │  │
│  │  git auto-sync           — version control, audit trail        │  │
│  └────────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │               Heartbeat System (Expand)                        │  │
│  │                                                                │  │
│  │  Every 30 min:  Check unread email, upcoming calendar          │  │
│  │  6:20 AM:       Morning briefing via Telegram                  │  │
│  │  Evening prior: Tomorrow's meeting confirmations               │  │
│  │  Weekly:        Calendar review, loose ends sweep              │  │
│  │  Pipeline:      Check for stale prospects, suggest outreach    │  │
│  └────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────┘
```

### What Changes from Current Setup

| Component | Current (Binary Wrapper) | Target (MCP-Native) |
|-----------|------------------------|---------------------|
| Gmail read | `gog-email-read.sh` → `gog` CLI | `google-workspace-mcp` → `gmail.search` / `gmail.read` |
| Gmail send | `gog gmail send --body-html` via exec-approval | `google-workspace-mcp` → `gmail.send` via ClawBands ASK |
| Calendar read | `gog-cal-read.sh` → `gog` CLI | `google-workspace-mcp` → `gcal.list` / `gcal.get` |
| Calendar create | `gog cal create` via exec-approval | `google-workspace-mcp` → `gcal.create` via ClawBands ASK |
| Read/write approval | exec-approvals.json (194 entries) | ClawBands ALLOW/ASK/DENY policy |
| Verification | Lobster workflow → verify-with-opus.sh → openclaw.invoke | OpenClaw sub-agent call to Opus (native llm-task) |
| iMessage | Not implemented | BlueBubbles channel (first-party) |
| Salesforce | Not implemented | `salesforce` ClawHub skill |
| Google Sheets | Not implemented | `google-workspace-mcp` → sheets tools |
| RingCentral | Partially implemented (custom) | Keep current + add MCP wrapper |
| Uber | Not implemented | Custom MCP or reminder-based |

### What Stays the Same

- **SOUL.md** — personality, voice, banned phrases
- **AGENTS.md** — agent roles, model assignment, escalation rules
- **Memory system** — daily notes, reference files, MEMORY.md, git sync
- **Follow-up tracker** — business-day logic, status management
- **Relationship manager** — people context, dynamics, history
- **Telegram as Dave's primary channel** — already working
- **Heartbeat system** — already working (will expand scope)
- **Approval pattern** — reads auto, sends to Dave. Same concept, cleaner implementation

---

## Part 4: Integration Architecture

### Tier 1: Immediate (Available as MCP Servers)

**google-workspace-mcp** (taylorwilsdon/google_workspace_mcp — independent MCP server, 696 stars, v1.11.2)
- Gmail: search, get, batch-get, send, thread, labels, batch-labels, modify-labels, manage-label, draft, batch-thread, auth (12 tools)
- Calendar: list-calendars, get-events, create-event, modify-event, delete-event (5 tools)
- Plus: Sheets, Drive, Docs, Slides, Forms, Chat, Tasks, Search tools
- **Important:** No `--reply-all` flag. Reply-all achieved by manually listing all To+CC recipients and using `thread_id` + `in_reply_to` + `references` for threading.
- **Auth:** OAuth 2.0 via Google Cloud Console
- **Install:** `uvx workspace-mcp --tools gmail calendar`

**salesforce** (ClawHub skill)
- Query: SOQL queries, describe objects, search
- Create: leads, contacts, opportunities, tasks, events
- Update: stage changes, field updates, notes
- Custom: proximity search via geolocation fields

**BlueBubbles** (first-party channel)
- Send/receive iMessages
- Tapbacks, threads, group management
- For: Tatum (close friend), Sarah (wife)

### Tier 2: Near-Term (Requires Some Setup)

**executive-assistant-skills** (mgonto/executive-assistant-skills)
- `meeting-prep`: Research attendees, prepare briefing
- `action-items`: Extract action items from meeting transcripts
- `executive-digest`: Daily/weekly summary generation
- `email-drafting`: Context-aware email composition

**ClawBands** (SeyZ/clawbands — standalone npm middleware, launched Feb 2026)
- Per-tool ALLOW/ASK/DENY policy with decision logging (append-only JSONL)
- Approval via Telegram (agent sends YES/NO question, user responds, agent calls `clawbands_respond`)
- Replaces: exec-approvals.json, wrapper scripts, PATH hacking
- **Install:** `npm install -g clawbands && clawbands init`
- **Config:** `~/.openclaw/clawbands/policy.json`

**RingCentral** (existing integration to enhance)
- Current: partially working custom skill
- Target: MCP wrapper for send_sms, call_status, voicemail

### Tier 3: Future (Custom Development Required)

**DocuSign MCP**
- Agreement sending, status tracking, template management
- For: proposal workflow automation

**Uber MCP** (or simpler approach)
- Ride estimates, ride requests, status tracking
- Start simple: time-based reminders ("Book Uber at 2:15 for 2:45 meeting")
- Evolve to: API-based with ride estimates and one-tap booking

**Custom Tools MCP**
- `proximity_search`: Salesforce geo-query for "Who else can I see near X?"
- `travel_log_update`: Google Sheets append for travel tracking
- `proposal_generator`: Template-based 1-page proposal creation
- `pipeline_dashboard`: Salesforce pipeline summary for morning briefing

---

## Part 5: Mapping the Executive Sales Assistant Role

The job description Dave shared defines the full scope of what Amber will eventually handle. Here's how each responsibility maps to the architecture:

### Calendar & Travel Management

| Responsibility | Implementation |
|---------------|---------------|
| Master Dave's calendar, identify openings | `google-workspace-mcp` → gcal.list + gcal.free-busy |
| Schedule & confirm meetings | `gcal.create` + confirmation emails via `gmail.send` |
| Book Uber rides | Uber MCP or reminder-based via Telegram |
| Drive-or-Uber decision | Distance calculation + parking lookup + time analysis |
| Maintain travel log | `google-workspace-mcp` → sheets.append |
| Find travel slots for road trips | gcal.free-busy + Salesforce geo-query |
| Confirm tomorrow's meetings | Heartbeat task: email/call confirmations evening prior |

### ProActive Sales Process

| Responsibility | Implementation |
|---------------|---------------|
| Maintain ProActive Sales Matrix | Salesforce opportunities + custom fields |
| Schedule ~2 qualified meetings/week | Salesforce pipeline query → outreach drafting |
| Research prospects before meetings | Web search + Salesforce history + LinkedIn |
| Prepare discovery meeting briefings | `meeting-prep` skill + custom research |
| Post-meeting follow-up emails | `action-items` skill → `email-drafting` skill |
| Generate 1-page proposals | Template-based custom tool |
| Send agreements via DocuSign | DocuSign MCP (Tier 3) |
| Track pipeline stages | Salesforce opportunity updates |
| "Who else can I see?" | Salesforce proximity search + route optimization |

### Account Management

| Responsibility | Implementation |
|---------------|---------------|
| Project kickoff coordination | Basecamp project creation + team notifications |
| Ongoing delivery monitoring | Basecamp to-do tracking + heartbeat checks |
| QBR scheduling | Calendar + template preparation |
| Renewal tracking | Salesforce renewal dates + follow-up automation |

### Communications

| Responsibility | Implementation |
|---------------|---------------|
| Email management (dave@mindfire.com) | Gmail monitoring + triage + draft responses |
| Internal comms (Carissa, employees) | RingCentral SMS/call + email |
| Personal contacts (Tatum, Sarah) | BlueBubbles iMessage |
| LinkedIn monitoring | Web scraping or LinkedIn API (limited) |
| Press/speaking triage | Email inbox monitoring + opportunity scoring |

### Follow-Up Engine

| Responsibility | Implementation |
|---------------|---------------|
| "Go after loose ends" | Follow-up tracker + Gmail thread analysis |
| Escalation chains | Email → email → phone (RingCentral) |
| Business-day timing | Already implemented in follow-up-tracker.md |
| Stale deal detection | Salesforce last-activity-date queries |

---

## Part 6: Implementation Roadmap

### Phase 0: Fix Current Issues (This Weekend — 1 day)
*Continue the batch fix plan already in progress*

- [ ] Standardize email signature (exact HTML block)
- [ ] Enforce `--body-html` harder (pre-send checklist)
- [ ] Add scripts directory to PATH on Amber's machine
- [ ] Restart gateway to pick up changes
- [ ] Verify email sends are working reliably

### Phase 1: MCP Migration — Gmail & Calendar (Week 1)

**Goal:** Replace all gog binary wrappers with `google-workspace-mcp` skill.

Steps:
1. Install `google-workspace-mcp` from ClawHub
2. Configure OAuth credentials (reuse existing)
3. Update `openclaw.json` to register MCP server
4. Install ClawBands middleware
5. Configure ALLOW/ASK/DENY policies
6. Update AGENTS.md tool references (MCP tool names instead of gog commands)
7. Update email-send/SKILL.md to use MCP tool calls instead of gog CLI
8. Update email-read/SKILL.md similarly
9. Update calendar skills similarly
10. Test: read email, draft reply, Dave approves, send — all via MCP
11. Remove: gog wrapper, gog-real, gog-email-read.sh, gog-cal-read.sh, gog-email-tag.sh
12. Remove: exec-approvals.json entries related to gog

**Success criteria:** Zero gog CLI calls. All email/calendar via MCP. ClawBands handles approval.

### Phase 2: Salesforce + Google Sheets (Week 2)

**Goal:** Connect CRM and spreadsheet data.

Steps:
1. Install `salesforce` skill from ClawHub
2. Configure Salesforce OAuth (Dave provides credentials)
3. Test: query contacts, query opportunities, describe objects
4. Add Salesforce tools to ClawBands policy (query = ALLOW, update = ASK)
5. Enable Google Sheets via `google-workspace-mcp` (already bundled)
6. Create travel log template in Google Sheets
7. Test: append travel log entry, read pipeline data
8. Create `proximity_search` custom tool (Salesforce SOQL with geo fields)
9. Update morning briefing to include pipeline summary

**Success criteria:** Amber can query Salesforce, update pipeline, and maintain travel log.

### Phase 3: BlueBubbles + Meeting Prep (Week 3)

**Goal:** iMessage integration and discovery meeting preparation.

Steps:
1. Set up BlueBubbles server on Amber's Mac
2. Configure as OpenClaw channel
3. Add iMessage tools to ClawBands (send = ASK)
4. Test: send iMessage to test number, receive confirmation
5. Install `executive-assistant-skills` suite
6. Configure `meeting-prep` skill with Dave's preferences
7. Configure `action-items` skill
8. Test: paste meeting transcript → extract action items → draft follow-ups
9. Integrate meeting prep into heartbeat (prep briefing 1 hour before meetings)

**Success criteria:** Amber can text Tatum/Sarah via iMessage. Amber preps for meetings automatically.

### Phase 4: Sales Process Integration (Week 4)

**Goal:** ProActive Sales Process support.

Steps:
1. Add ProActive Sales Process knowledge to MEMORY.md (terminology, stages, methodology)
2. Create Salesforce custom fields or use existing for pipeline stages
3. Build pipeline review heartbeat task (weekly)
4. Build "Who else can I see?" proximity search
5. Build prospect outreach drafting workflow
6. Build post-meeting follow-up automation (transcript → action items → emails)
7. Test: full cycle from discovery meeting to follow-up to proposal stage

**Success criteria:** Amber actively manages the prospect pipeline and suggests next actions.

### Phase 5: Full Chief of Staff (Weeks 5-8)

**Goal:** Complete Executive Sales Assistant replacement.

Steps:
1. DocuSign integration for agreement sending
2. Uber integration (start with reminders, evolve to API)
3. Drive-or-Uber decision logic
4. LinkedIn monitoring (likely manual with Amber helping analyze)
5. Public inbox management (dave@mindfire.com)
6. Press/speaking opportunity triage
7. QBR preparation templates
8. Renewal tracking automation
9. Tomorrow's meeting confirmation workflow
10. Weekly calendar review automation

**Success criteria:** Amber handles 80%+ of the Executive Sales Assistant job description.

---

## Part 7: What Was Right and Wrong in the Original Reports

### Architecture Comparison Report (2026-03-05)

| Section | Verdict |
|---------|---------|
| Executive Summary: "Migrate off OpenClaw" | **WRONG** — should stay on OpenClaw, fix approach |
| "38 hours debugging" analysis | **RIGHT** — the time was real, but caused by wrong approach |
| "Binary-path exec-approval is primitive" | **RIGHT** — but ClawBands solves this natively |
| "gog CLI is wrong for AI agents" | **RIGHT** — MCP is the correct pattern |
| "Lobster workflows are fragile" | **RIGHT** — MCP eliminates need for Lobster |
| "Keep memory system" | **RIGHT** — still the recommendation |
| "Keep SOUL.md" | **RIGHT** — still the recommendation |
| "Python orchestrator" proposal | **WRONG** — rebuilds what OpenClaw already provides |
| "5-7 days to migrate" estimate | **WRONG** — would actually be 4-6 weeks |
| Feature comparison table | **PARTIALLY RIGHT** — MCP columns accurate, OpenClaw column underestimates |
| n8n as alternative | **WORTH KNOWING** — but not recommended given OpenClaw's ecosystem |

### Ecosystem Research Report (2026-03-06)

| Section | Verdict |
|---------|---------|
| "You are pioneering" | **RIGHT** — Amber's scope is genuinely novel |
| OpenClaw context (corrected) | **RIGHT** (after correction) |
| Community pain points analysis | **RIGHT** — these are universal |
| Verification sub-agent pattern | **RIGHT** — sound architecture |
| Memory system assessment | **RIGHT** — appropriate for current scale |
| Architecture tier assessment | **RIGHT** — Amber is Tier 3-4 |
| Scope limited to "email assistant" | **WRONG** — massively underestimated Amber's full role |

---

## Part 8: Risk Assessment

### Risks of the MCP-Native Approach

1. **Skill compatibility:** `google-workspace-mcp` and `salesforce` skills may have bugs or missing features. Mitigation: test thoroughly in Phase 1 before removing gog wrappers.

2. **ClawBands maturity:** Community middleware, not first-party OpenClaw. Mitigation: review source code, have fallback approval mechanism.

3. **OpenClaw gateway instability:** Known issue in v2026.3.x. Mitigation: this is independent of MCP vs binary approach; same risk either way.

4. **MCP skills not covering edge cases:** Some gog CLI features may not have MCP equivalents. Mitigation: keep gog as emergency fallback, don't delete it.

5. **BlueBubbles reliability:** iMessage integration depends on macOS + BlueBubbles server. Mitigation: have email/SMS fallback for personal contacts.

### What Could Still Justify Migration Later

If any of these prove true, revisit the "migrate off OpenClaw" recommendation:
- ClawBands doesn't actually work for tool-level approval
- `google-workspace-mcp` has critical bugs that aren't fixed
- OpenClaw gateway instability worsens and blocks production use
- OpenClaw project goes dormant after OpenAI acquisition

---

## Part 9: Immediate Next Steps

1. **Complete the batch fix plan** (email formatting, signature, PATH) — already in progress
2. **Research `google-workspace-mcp`** — read docs, check GitHub issues, verify it handles email threading and HTML bodies
3. **Research ClawBands** — verify tool-level approval actually works, read source code
4. **Create GitHub issue for Phase 1** — MCP migration for Gmail and Calendar
5. **Back up current working setup** — git tag the current state before making changes

---

## Sources

- [OpenClaw GitHub](https://github.com/openclaw/openclaw) — 247K stars, 47.7K forks
- [OpenClaw Official Site](https://openclaw.ai/)
- [CrowdStrike Security Analysis](https://www.crowdstrike.com/en-us/blog/what-security-teams-need-to-know-about-openclaw-ai-super-agent/)
- [Milvus Complete Guide](https://milvus.io/blog/openclaw-formerly-clawdbot-moltbot-explained-a-complete-guide-to-the-autonomous-ai-agent.md)
- [DigitalOcean Guide](https://www.digitalocean.com/resources/articles/what-is-openclaw)
- [Fast Company Profile](https://www.fastcompany.com/91495511/i-built-an-openclaw-ai-agent-to-do-my-job-for-me-results-were-surprising-scary)
- [VentureBeat on OpenAI Acquisition](https://venturebeat.com/technology/openais-acquisition-of-openclaw-signals-the-beginning-of-the-end-of-the)

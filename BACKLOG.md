# Main Agent - Feature Backlog

## High Priority

### Phase 1: MCP Migration — Gmail & Calendar (NEXT)
- **Goal:** Replace all gog CLI binary wrappers with google-workspace-mcp + ClawBands
- **Prep work:** DONE on `phase1-mcp-migration` branch (migration guide, policy template, MCP skill files, server config)
- **Key tools:**
  - `google-workspace-mcp` (taylorwilsdon/google_workspace_mcp, 696 stars, v1.11.2) — independent MCP server
  - `ClawBands` (SeyZ/clawbands, launched Feb 2026) — standalone ALLOW/ASK/DENY middleware
- **Remaining (needs Amber's machine):**
  - [ ] Install google-workspace-mcp (`uvx workspace-mcp`)
  - [ ] Configure OAuth credentials (Google Cloud Console)
  - [ ] Register MCP server in openclaw.json
  - [ ] Install ClawBands (`npm install -g clawbands`)
  - [ ] Apply clawbands-policy.json
  - [ ] Test: read email via MCP (should auto-approve)
  - [ ] Test: send test email via MCP (should prompt Dave via Telegram)
  - [ ] Test: reply threading (thread_id + in_reply_to + references — NO --reply-all flag)
  - [ ] Test: calendar read and create via MCP
  - [ ] Switch skill files from SKILL.md to SKILL-MCP.md
  - [ ] Remove gog wrapper scripts (keep gog-real as emergency fallback)
- **Eliminates:** gog wrapper scripts, PATH hacking, exec-approvals.json gog entries, Lobster workflows, hard binary copies
- **Does NOT change:** SOUL.md, AGENTS.md personality, approval pattern, verify-with-opus, memory system, Telegram channel
- **Addresses issues:** #8 (openclaw.invoke not found), #9 (allowlist), #10 (Lobster dead code), #11 (threading), #13 (gog-real breaks after brew)
- **Risk mitigation:** Keep gog-real, rollback to `main` / tag `baseline-email-working-2026-03-06`
- **References:** `docs/MCP-MIGRATION-GUIDE.md`, `config/clawbands-policy.json`, `config/mcp-servers.json`
- **Status:** Prep branch created 2026-03-06. Awaiting Dave for machine-side installation.

### Replace Custom Solutions with OpenClaw Official Tools (IMMEDIATE)
- **Gmail PubSub Setup:** Replace custom email-processor with `openclaw webhooks gmail setup` for real-time push notifications (vs 5min polling)
- **Cost Tracking Replacement:** Replace `scripts/daily-cost-tracker.py` with built-in `/usage cost`, `/status`, `openclaw status --usage` commands  
- **OpenAI Codex Research:** Set up Brave Search API (`openclaw configure --section web`) and research real user experiences on OpenAI Codex subscription vs API pricing on Reddit/Twitter/GitHub
- **Memory System Exploration:** Investigate `openclaw memory` (semantic search/indexing) to replace manual daily notes system
- **Hooks System Review:** Check `openclaw hooks` for automation we're doing manually
- **Session Management:** Explore built-in `openclaw sessions`, `openclaw agents` tools vs manual monitoring
- **Impact:** 50-70% time savings by using official tooling instead of reinventing wheels
- **Priority:** IMMEDIATE - this is pure efficiency gain with zero downside
- **Status:** Identified 2026-03-02, "Official First" rule added to AGENTS.md

### SMS MMS/Image Support
- **Problem:** Images sent via SMS don't come through to the plugin
- **Need:** Support MMS inbound (image download + display to agent)
- **Discovered:** 2026-03-02, Dave tried sending an image via SMS

### LinkedIn Sub-Agent
- **Need:** Monitor Dave's LinkedIn for post engagement, comments, connection requests
- **Why:** LinkedIn is now a public channel for Amber (post went live 2026-03-02). Need to track who's engaging, surface context about commenters/likers, and help Dave respond strategically.
- **Capabilities needed:** Read post metrics, comments, new connections. Cross-reference with MEMORY.md for relationship context.
- **Blocked by:** LinkedIn API access or browser automation approach TBD

### Gateway Self-Recovery System (RESOLVED)
- **Status:** RESOLVED 2026-03-02. `openclaw gateway restart` works from agent session. Session survives restart.
- **Success Criteria:** I can restart broken gateway without requiring Dave's manual intervention
- **Priority:** HIGH - Essential for operational reliability when Dave is unavailable
- **Status:** Identified during March 1 group chat troubleshooting

### Open Source Intelligence Comparison (REQUIRED RESEARCH)
- **Goal:** Evaluate reasoning ability and intelligence of open source models vs Claude
- **Purpose:** Understand capability gaps before considering any cost optimization deployment
- **Framework created:** INTELLIGENCE-COMPARISON.md with comprehensive 6-category evaluation system
- **Key question:** Are open source models actually smart enough for our business use cases?
- **Models to evaluate:** Mixtral 8x7B, Llama 2 70B, Code Llama 34B, Yi 34B, Mistral 7B
- **Test methodology:** Blind testing on real business scenarios, 1-10 intelligence scoring
- **Categories:** Reasoning, comprehension, strategic thinking, communication, technical precision, nuanced understanding  
- **Priority:** Complete before any model deployment decisions
- **Status:** Research framework complete, testing to be scheduled - Strategic Business Impact

### Business Intelligence Sub-Agent
- **Requested:** Dave specifically requested this morning from Google Alerts digest
- **Function:** Monitor Google Alerts → research companies/people → craft strategic outreach  
- **Real triggers:** PreSmart Solutions, "Phygital Imperative" opportunities identified
- **Integration:** Works with Relationship Manager for strategic outreach coordination
- **Business value:** Turn market intelligence into relationship building and partnership opportunities

### Multi-Agent Workflow Integration Testing  
- **Real-world validation:** March 4-5 follow-ups will test Email → Relationship → Follow-Up workflow
- **Event coordination testing:** Glen/Peter responses will test Relationship → Event Manager coordination
- **Iteration based on usage:** Refine sub-agent interactions based on actual business scenarios
- **Error handling improvement:** Better sub-agent error recovery and cross-agent communication

### Sales Pipeline Context Import from Claude Projects (CRITICAL)
- **Problem:** Dave has detailed context on each sales deal in separate Claude projects (Warren CAT, SEprint, Advertisers Printing, others). I can't access these, so I'm flying blind on deal stage, size, history, and contacts.
- **Goal:** Get pipeline context into my memory so I can properly support sales follow-ups, draft informed emails, and track deals.
- **Options to explore:**
  1. Dave exports/copies project context into files I can index (memory/reference/sales/)
  2. Build a simple intake flow: Dave pastes key deal info, I structure and store it
  3. API access to Claude projects (if available)
  4. CRM integration (HubSpot, Salesforce, or simple file-based tracker)
- **Immediate need:** Warren CAT, SEprint, Advertisers Printing deal details
- **Success criteria:** I know deal size, stage, key contacts, history, and next steps for each active deal
- **Priority:** HIGH - directly impacts revenue. Can't close deals I don't understand.
- **Status:** Identified 2026-03-02

### Model Failover Configuration
- **Problem:** Anthropic Opus had elevated errors (2026-03-02), subagent hung for 12 min
- **Goal:** Auto-fallback to GPT-4o or Sonnet when primary model is degraded
- **Status:** Identified 2026-03-02

### RingCentral Real-Time Optimization
- **Dave's request:** "5 minutes too long for real-time team messaging"
- **Technical challenge:** Solve rate limiting for 30-60 second checking frequency
- **Alternatives:** WebSocket notifications (permissions solved) or exponential backoff polling
- **Business impact:** True real-time team collaboration instead of 5-minute delays

### GitHub Auth & Workspace Remote
- **Problem:** No `gh` auth configured, no SSH keys. Can't push workspace commits to GitHub or file issues.
- **Need:** Dave to either create a PAT or run `gh auth login` on the machine.
- **Benefit:** Dave can see workspace changes on GitHub, I can file issues on openclaw/openclaw.
- **Status:** Parked, do when convenient.

### Cross-Context Outbound for Plugin Channels (Platform Bug)
- **Problem:** Gateway doesn't pass resolved `account` object to plugin `sendText`/`sendMedia` on cross-context sends. Error: `Cannot read properties of undefined (reading 'configured')`
- **Affects:** Both ringcentral-team and ringcentral-sms outbound from non-native sessions (e.g. Telegram→RC)
- **Impact:** Low for now. Inbound + same-session replies work fine. Only blocks proactive cross-channel sends.
- **Likely cause:** Platform bug in OpenClaw delivery code for plugin channels.
- **Status:** Parked. File GitHub issue when gh auth is set up.

### Orphan Transcript Cleanup
- **Problem:** 255 orphan transcript files in `~/.openclaw/agents/main/sessions/` not referenced by sessions.json
- **Impact:** Disk space only, low priority.
- **Fix:** TBD, may be a doctor command or manual cleanup.

## Medium Priority - System Enhancement

### Advanced Memory Management
- **Communication History Database:** Systematic tracking of all cross-platform conversations (requested Feb 28)
- **Cross-session context:** Better continuity between Telegram, RingCentral, and email contexts
- **Relationship progression tracking:** Deeper analytics on relationship development over time
- **Historical pattern analysis:** Learn from past interactions to improve future responses

### Sub-Agent Orchestration Refinement
- **Dynamic sub-agent spawning:** Auto-spawn appropriate sub-agents based on message content
- **Inter-agent communication:** Direct sub-agent to sub-agent coordination when appropriate  
- **Load balancing:** Distribute work optimally across sub-agents for performance
- **Dependency management:** Handle cases where one sub-agent depends on another's output

### Notification System Enhancement
- **Smart notification batching:** Reduce notification fatigue while ensuring important items get through
- **Context-aware priorities:** Dynamic priority adjustment based on business context and timing
- **Cross-platform notification:** Coordinate alerts across Telegram, RingCentral, and email
- **Escalation workflows:** Automatic escalation for repeatedly missed items

## Low Priority - Quality of Life

### Development Tools & Monitoring
- **Sub-agent performance dashboard:** Monitor token usage, response times, success rates across all agents
- **Integration testing framework:** Automated testing of sub-agent workflows  
- **Configuration management:** Centralized config for all sub-agents with version control
- **Debugging tools:** Better visibility into sub-agent decision making and workflow execution

### Advanced Scheduling Intelligence  
- **AI-powered meeting optimization:** Learn Dave's preferences and suggest optimal meeting patterns
- **Cross-timezone coordination:** Intelligent scheduling for contacts across time zones
- **Meeting preparation automation:** Generate prep briefs with participant context automatically
- **Calendar analytics:** Insights into time allocation and meeting effectiveness

### Content Generation & Templates
- **Email template system:** Pre-approved templates for common business scenarios
- **Presentation support:** DSCOOP and other event presentation preparation assistance
- **Business development content:** Automated generation of partnership proposals and follow-up materials
- **Industry intelligence reports:** Automated competitive analysis and market intelligence summaries

## Completed Features
- ✅ Multi-agent architecture with specialized sub-agents
- ✅ Email processing automation with relationship intelligence
- ✅ RingCentral integration with full business context  
- ✅ Calendar management with Dave's preferences
- ✅ Event management for strategic networking (DSCOOP Edge 2026)
- ✅ Follow-up automation with business day rule enforcement
- ✅ Speaker attribution system for clear recommendation sources
- ✅ Development tracking standards across all agents
- ✅ Workspace cleanup and obsolete code archival
- ✅ Token cost optimization through sub-agent architecture

## Current Integration Focus Areas

### March 2026 Real-World Testing  
- **Follow-up system:** March 4-5 due dates (Tiffany Todd, Glen Adams, Peter van Teeseling, Chris Lien)
- **Event coordination:** DSCOOP Edge March 7-12 strategic networking execution
- **Cross-agent workflows:** Email detection → Relationship context → Event/Follow-up coordination
- **Business outcome tracking:** Partnership advancement, meeting success, relationship progression

### Architecture Refinement Priorities
- **Performance optimization:** Monitor and optimize sub-agent token usage and response times
- **Error handling:** Improve robustness of inter-agent communication and failure recovery  
- **Scalability planning:** Prepare architecture for additional sub-agents (Business Intelligence, others)
- **Context management:** Balance shared context vs agent-specific specialization

## Strategic Objectives
- **Business relationship focus:** Architecture supports Dave's relationship-driven work style
- **Efficiency without sacrifice:** Maintain or improve service quality while reducing token costs
- **Scalable growth:** Add new capabilities through specialized sub-agents rather than monolithic expansion
- **Real-world validation:** Every feature tested with actual business scenarios and outcomes

## Rejected/Won't Do - Architectural Decisions
- **Monolithic expansion:** No return to single-agent handling everything
- **Sub-agent per contact:** Too granular, relationship patterns work better  
- **Automatic external actions:** All outbound communications require Dave's approval
- **Complex workflow engines:** Keep sub-agent interactions simple and understandable
- **Feature creep:** Focus on business-critical capabilities rather than convenience features

---

*This backlog focuses on strategic business value and architectural refinement, ensuring the multi-agent system serves Dave's relationship-driven business needs effectively.*
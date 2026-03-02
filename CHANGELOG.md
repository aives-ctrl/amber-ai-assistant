# Main Agent - Change Log

## 2026-03-01 - Family Coordination & Calendar Optimization (v2.7)

### Added: Family Coordination System
- **USER.md updated** with complete family member names, relationships, school, activities
- **Calendar Manager** updated with family logistics, scheduling constraints, search methodology
- **Office arrival constraint:** NEVER schedule work before 6:20 AM (system-wide rule)
- **Consolidated prep blocks:** ONE event with all topics instead of individual meetings
- **Tesla FSD integration:** Physical addresses required for all kid events

### Added: Topic Management System  
- **Hashtag-based topic switching:** `#topic-name message content`
- **Acknowledgment protocol:** Amber acknowledges switch and focuses on new topic
- **Documented in AGENTS.md** as standard conversation management pattern

### Added: Messaging Style Guidelines
- **2-3 sentences max** in chat/messaging contexts (Telegram, RingCentral)
- **Use abbreviations and shorthand** (btw, w/, pls, thx, lmk, rn, etc.)
- **No formal bullet points** in casual messaging
- **Save assistant voice for emails** — be conversational in chats

### Lessons Learned & Mistakes Fixed
- ❌ Scheduled prep before office arrival (5:30 AM) → Fixed: 6:20 AM minimum
- ❌ Created individual prep meetings → Fixed: consolidated blocks
- ❌ Missed calendar events due to pagination → Fixed: better search methodology
- ❌ Missed Zoom links by only checking location field → Fixed: check all link fields
- ❌ Too verbose in group chats → Fixed: messaging style guidelines added to SOUL.md

## 2026-03-01 - Email Processor Critical Fix & Security Hardening (v2.6)

### Fixed: Email Processor Major Scope Bug  
- **Critical Issue:** Email Processor only processed emails FROM Dave (`from:daver@mindfireinc.com`)
- **Impact:** Missing ALL direct emails from Glen Adams, Peter van Teeseling, Anthropic, business contacts
- **Fix:** Changed search to `gog gmail search 'is:unread -label:Handled'` (ALL emails TO Amber)
- **Also Fixed:** Broken `gog gmail messages search` command (removed "messages")
- **Enhanced:** Added URGENT_SERVICE detection for service alerts like `[action needed]`
- **Root Cause:** Anthropic API alert missed due to both search command failure AND wrong scope

### Result
- **Email Processor now catches ALL incoming emails** to aives@mindfiremail.info
- **Service alerts properly flagged** as urgent instead of missed entirely
- **Business correspondence processed** instead of ignored
- **Architecture fixed:** Email processing works as originally intended

## 2026-03-01 - Security Hardening & Error Privacy (v2.5)

### Added: Comprehensive Group Chat Security
- **Sandbox enforcement:** Group chats now run in Docker sandbox with messaging-only tools
  - Cannot access calendar (`gog calendar` blocked)
  - Cannot access files, email, exec commands  
  - Cannot access any sensitive tools or data
- **Error message privacy:** Added context-aware error handling rules
  - Group sessions: Generic error messages only ("I'm having technical difficulties")
  - Never expose API errors, credit status, model names, system details to external users
  - Technical details routed privately to Dave via `sessions_send`
  - DM sessions: Full error details preserved for troubleshooting

### Security Configuration Applied
```json
"sandbox": {
  "mode": "non-main",
  "scope": "session", 
  "workspaceAccess": "none"
},
"tools": {
  "sandbox": {
    "tools": {
      "allow": ["group:messaging", "group:sessions"],
      "deny": ["gog", "exec", "read", "write", "calendar", etc...]
    }
  }
}
```

### Impact
- **System-level enforcement:** External users cannot trigger calendar/file access even via prompt injection
- **Privacy protection:** No more accidental disclosure of internal system status or Dave's data
- **Error security:** Technical failures no longer leak sensitive information to group chats
- **DM functionality preserved:** Private coordination between Dave and Amber unchanged

## 2026-03-01 - Cross-Session Coordination & Group Chat Fix (v2.4)

### Added: Multi-Session Coordination System
- **Fixed group chat visibility:** Set `tools.sessions.visibility: "all"` in OpenClaw config
  - Allows DM session to monitor group chat sessions using `sessions_history`
  - Essential for multi-context experiments and coordination
- **Message routing clarification:** Documented distinction between internal vs external messaging
  - `sessions_send` = Internal OpenClaw messages between sessions
  - `message` tool = External platform messages (Telegram, Discord, etc.)
- **Cross-session patterns documented:** Added coordination patterns to AGENTS.md
  - Private strategy discussions + group chat engagement simultaneously
  - Monitor multiple conversations from one session
- **Multi-context experiments enabled:** Can now run experiments with private coaching + group interaction
- **IDENTIFIED CRITICAL ISSUE:** Gateway self-recovery failure - `kill -9` broke gateway, couldn't restart from agent session, required manual terminal intervention (added to backlog as HIGH PRIORITY)

## 2026-03-01 - Cost Monitoring + Model Failover + Approval Cascade (v2.3)

### Added: Precise Cost Monitoring
- **Anthropic pricing configured:** Sonnet $3/$15, Opus $15/$75 per 1M tokens (input/output) in OpenClaw config
- **Precise calculator:** Custom Python script calculates exact costs from session_status output
- **Report format:** "💰 Session: 173in/4kout → $0.333 | Opus | 70% context"
- **Enhanced HEARTBEAT.md:** 3x daily precise cost reports (every 4+ hours)
- **Smart tracking:** `memory/heartbeat-state.json` prevents spam, tracks calculation metadata
- **Context alerts:** Warns when session >80% context (suggests compaction)
- **Fixed config issues:** `openclaw doctor --fix` removed invalid loop detection keys
- **Secured config:** Fixed file permissions to mode 600 (was world-readable)
- **Tested working:** End-to-end cost calculation validated with current session data

## 2026-03-01 - Model Failover + Loop Detection + Approval Cascade (v2.2)

### Added: Model Failover & Loop Detection (OpenClaw Core Features)
- **Model Failover:** Added `agents.defaults.model.fallbacks: ["anthropic/claude-opus-4-6"]`
  - If Sonnet fails/rate-limits → automatically falls back to Opus
  - Protects critical workflows (especially Relationship Manager on Opus)
  - Uses OpenClaw's built-in auth profile rotation + model fallback chains
- **Loop Detection:** Enabled `tools.loopDetection` with standard settings
  - Detects repetitive tool-call patterns (same tool, same inputs, repeated failures)
  - Prevents runaway token spend and lockups
  - 3-repeat threshold before warnings, 6-repeat threshold for blocking
- **Config Backup:** Original config saved as `openclaw-backup-20260301-110525.json`
- **Verification:** All changes tested, OpenClaw status confirmed working

## 2026-03-01 - Cron Delivery Fix + Approval Cascade (v2.1)

### Fixed: Heartbeat Notification Spam
- **Problem:** Email Processor and RingCentral Processor crons were trying to announce every HEARTBEAT_OK (every 5 minutes)
- **Solution:** Disabled announcement delivery (`--no-deliver`) for both cron jobs  
- **Keep:** Follow-Up Manager still announces (daily, usually has real content)
- **Result:** No more heartbeat spam - agents work quietly unless they find actual work

### Breaking Change: Three-Tier Approval System
All sub-agents converted from autonomous executors to proposal generators.

**New workflow:** Sub-Agent → Main Session (Amber reviews) → Dave (approves) → Execute

**Files created:**
- `APPROVAL-WORKFLOW.md` - master governance document with phased autonomy plan

**All 5 sub-agents updated to v2.0:**
- Email Processor: Proposes routing plans, only silently handles routine emails
- Calendar Manager: Read-only queries allowed, all writes are proposals with exact commands
- Relationship Manager: Drafts responses with strategic reasoning for review
- Follow-Up Manager: Reports status with proposed follow-up drafts
- Event Manager: Researches freely, proposes outreach and calendar actions

**Exception:** Email Processor may still silently mark routine emails as Handled (Phase 1 autonomy)

**Training Wheels:** System designed with phased removal - when confident, selective autonomy can be granted per agent/action type

### Calendar Fix: Correct gog Command Syntax
- Fixed `--title` → `--summary`, `--start` → `--from`, `--duration` → `--to`
- Calendar ID: `daver@mindfireinc.com` not `primary`
- Documented `--add-attendee` for preserving existing attendees
- Added event ID extraction from calendar list output

### Chris Lien Resolution
- Successfully added Christopher O'Brien to existing Monday sync (March 2nd, 12:00 PM)
- Confirmation email sent to Chris Lien
- Follow-up tracking updated, relationship data updated

## 2026-03-01

### Major Architecture Evolution - Multi-Agent System Implementation
- **Switched from monolithic to orchestrated delegation:** Replaced single-agent approach with specialized sub-agent system
- **Sub-agent architecture research:** Analyzed "Claude Skills and Subagents" article, identified OpenClaw capabilities underutilization
- **Model optimization:** Implemented strategic model switching (Sonnet default, Opus for complex planning)

### Sub-Agent System Deployment
**Email Processing Sub-Agent:**
- **Email Processor:** Mechanical email processing (scan, categorize, route) - every 5 minutes
- **Relationship Manager:** Strategic relationship intelligence with deep contact profiles
- **Integration:** Email → Relationship → strategic response pipeline

**Communication Sub-Agents:**  
- **RingCentral Processor:** Converted from standalone Python script to proper OpenClaw sub-agent
- **Frequency optimization:** Reduced from 1 minute (rate limits) to 5 minutes (stable)
- **Full context integration:** Business knowledge, memory files, tool access

**Calendar & Event Management:**
- **Calendar Manager:** Strategic scheduling with Dave's preferences (25-min meetings, morning focus)
- **Event Manager:** Strategic event networking, meetings AT events rather than around them
- **DSCOOP Edge 2026 profile:** March 7-12 Denver strategic networking plan

**Follow-Up Automation:**
- **Follow-Up Manager:** Automated response tracking with 3-business-day rule enforcement
- **Prevention system:** Blocks premature follow-ups (learned from Chris Lien/Tiffany Todd mistakes)  
- **Real-world testing:** March 4-5 follow-ups due (5 pending contacts)

### System Improvements
**Speaker Attribution System:**
- **Problem identified:** Dave couldn't distinguish between main agent vs sub-agent recommendations
- **Solution implemented:** SPEAKER-ATTRIBUTION.md framework with clear authority levels
- **Authority indicators:** Main Amber (full authority) vs Sub-agent reports vs System status vs Musings

**Development Tracking Standards:**
- **SUB-AGENT-STANDARDS.md:** CHANGELOG.md + BACKLOG.md requirement for all agents
- **Agent self-maintenance:** Each sub-agent owns its development roadmap and accountability
- **Consistent documentation:** Every agent tracks changes, features, and decisions

**Workspace Cleanup (March 1, 9:25 AM):**
- **Archived obsolete scripts:** 20+ old RingCentral iteration scripts moved to archive
- **Removed old LaunchAgents:** Cleaned up superseded ai.openclaw.ringcentral.ai.plist and gateway.plist
- **Documentation cleanup:** Archived outdated RINGCENTRAL-*.md files
- **Kept essential files:** notification-queue system (still active), reference implementations

### Architecture Principles Established
- **Orchestrated delegation:** Main agent coordinates, specialized sub-agents execute
- **Shared memory:** All agents access SOUL.md, MEMORY.md, MINDFIRE.md for consistency  
- **Context isolation:** Sub-agents run in isolated sessions to prevent main session context bloat
- **Business focus:** Architecture reflects Dave's relationship-driven work (events, partnerships, follow-ups)

### Real-World Integration Success
**Live testing validation:**
- **Email test:** Dave → Brian B + cc Amber correctly categorized and handled
- **Follow-up detection:** Brian Badillo response automatically detected and processed  
- **Event strategy:** Glen Adams meeting corrected from pre-DSCOOP to AT DSCOOP
- **Speaker attribution:** Clear identification of recommendation sources

### Token Economics & Cost Optimization
- **Sub-agent efficiency:** ~17k tokens per 5-minute check vs main session overhead
- **Model switching:** Strategic Opus use for complex planning, Sonnet for routine tasks
- **Context management:** Main session stays lightweight through sub-agent delegation
- **Estimated savings:** 60-70% token reduction through specialized worker pattern

## Architecture Evolution Summary
- **From:** Monolithic main session handling everything
- **To:** Orchestrated multi-agent system with specialized domains
- **Result:** Scalable, efficient, business-aligned assistant architecture
- **Pattern:** Progressive specialization while maintaining coordination and shared context

## Integration Status
- **Telegram:** Main coordination channel with full context
- **RingCentral:** Sub-agent with full business context and tool access  
- **Email:** Automated processing with relationship intelligence
- **Calendar:** Strategic scheduling with event management
- **Follow-ups:** Automated tracking with relationship context
- **Events:** Strategic networking optimization (DSCOOP Edge ready)

---

*This changelog documents the evolution from single-agent to multi-agent orchestrated system, establishing the architectural foundation for scalable business assistance.*
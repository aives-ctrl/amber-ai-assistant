# Email Processor - Change Log

## 2026-03-01 (v2.5) - CRITICAL BUG FIX: Service Alert Detection

### Fixed: Email Search Command Bug  
- **Critical Issue:** `gog gmail messages search` command was broken, returned no results
- **Fix:** Changed to `gog gmail search` (removed "messages" subcommand)
- **Impact:** Email Processor was missing ALL emails due to search failure

### Fixed: Email Scope Bug (MAJOR)
- **Critical Issue:** Email Processor only searched `from:daver@mindfireinc.com` (emails FROM Dave only)
- **Fix:** Changed to `gog gmail search 'is:unread -label:Handled'` (ALL emails TO Amber)
- **Impact:** Was missing ALL direct emails from Glen Adams, Peter van Teeseling, Anthropic, business contacts
- **Root Cause:** Wrong interpretation of scope - should process ANY email TO Amber, not just FROM Dave

### Enhanced: Urgency Detection Patterns
- **Added URGENT_SERVICE category** for service alerts, API issues, billing problems
- **Added URGENT_BUSINESS category** for meeting conflicts, client escalations
- **Detection patterns:** `[action needed]`, `disabled`, `suspended`, `expired`, `failed`
- **Service provider alerts:** Anthropic, OpenAI, Google, financial institutions  
- **Never handle service alerts as routine** - always flag for immediate attention

### Impact
- **Fixed:** Email Processor will now catch forwarded service alerts
- **Enhanced:** Better urgency detection prevents missing critical notifications
- **Tested:** Confirmed fixed search finds the missed Anthropic API alert

## 2026-03-01 (v2.1) - CRON DELIVERY FIX

### Fixed: Heartbeat Notification Spam
- **REMOVED:** Announcement delivery for HEARTBEAT_OK messages
- **CHANGED:** Cron job delivery mode from "announce" to "none"
- **REASONING:** Every 5-minute HEARTBEAT_OK was trying to notify Dave, causing spam
- **RESULT:** Quiet operation when no emails to process, approval cascade handles real notifications

## 2026-03-01 (v2.0) - APPROVAL CASCADE

### Breaking Change: Approval Cascade Architecture
- **REMOVED:** Direct `sessions_spawn` to other sub-agents
- **ADDED:** Structured plan output format for main session review
- **CHANGED:** All non-routine emails produce proposals, not actions
- **KEPT:** Silent handling of routine emails (mark as Handled)
- **NEW:** Explicit plan format with category, routing recommendation, extracted details
- **Governance:** Three-tier approval: Email Processor → Main Session → Dave → Execute

## 2026-03-01 (v1.1)

### Added: Meeting/Scheduling Email Detection & Calendar Routing
- **New category:** MEETING/SCHEDULING EMAILS - detects emails containing meeting logistics
- **Calendar Manager routing:** Spawns Calendar Manager sub-agent for scheduling actions
- **Dual routing:** Emails that are both meeting + contact route to BOTH Calendar Manager and Relationship Manager
- **Detection keywords:** "available", "schedule", "meeting", "calendar", dates/times with names, "add [person] to", "reschedule"
- **Structured context:** Passes WHO/WHEN/WHERE/ACTION to Calendar Manager for precise execution
- **Root cause fix:** Previously, meeting coordination emails only went to Relationship Manager, missing the calendar action entirely (e.g., Chris Lien response about adding Christopher O'Brien to existing meeting)

## 2026-03-01 (v1.0)

### Created v1.0
- **Initial deployment** as OpenClaw sub-agent
- **Mechanical processing only:** Scan inbox, categorize routine vs contact emails
- **Route contact emails** to Relationship Manager for strategic responses  
- **Cron schedule:** Every 5 minutes
- **Architecture:** Isolated OpenClaw sessions, announces to Telegram
- **Scope:** aives@mindfiremail.info inbox only (Amber's account)

### Architecture Decisions
- **Separated from relationship management:** Pure mechanical dispatcher
- **Contact routing:** Sends contact emails to Relationship Manager sub-agent
- **Routine handling:** Silently processes system notifications, marks as "Handled"
- **No strategic decisions:** Escalates all contact interactions
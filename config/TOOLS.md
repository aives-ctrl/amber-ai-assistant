# TOOLS.md - Local Notes

Environment-specific config. Skills define how tools work; this is your cheat sheet.

### Zoom (Dave's PMI)
- Link: https://mindfire.zoom.us/j/4630269255?pwd=VE9McTZFRXlMV01MTEFweklnbDFWZz09
- Meeting ID: 463 026 9255 | Passcode: boom!
- Phone: +1 312-626-6799 (passcode 541630)

### Message Routing
- `sessions_send` → internal OpenClaw messages between sessions
- `message` tool → external platform messages (Telegram, Discord, etc.)
- Session visibility: `tools.sessions.visibility: "all"` enabled

### Calendar Access
- Dave's calendar ID: `daver@mindfireinc.com` (shared to my account)
- List events: `gog cal events daver@mindfireinc.com --from X --to Y` (NOT `events ls`)
- Create events: `gog cal create daver@mindfireinc.com --summary ... --from ... --to ...`
- My calendar (aives@mindfiremail.info) has no primary events; always use Dave's ID

### Exec Approvals (gog/email guardrail) - ACTIVE
- `gog` is NOT on the exec allowlist. Every `gog` command requires Dave's approval via Telegram.
- Dave receives a 🔒 prompt with full UUID, command details, and expiry.  
- Dave approves with `/approve <FULL-UUID> allow-once` (NEVER `allow-always` for gog).
- **IMPORTANT:** Always use `timeout: 3600` (60 min) on gog exec calls so Dave has time to approve.
- **NOTE:** Cannot auto-send copy-paste approval lines (approval forwarding bypasses main session).
- All other binaries in `/bin/*`, `/usr/bin/*`, `/usr/local/bin/*` (except gog) are allowlisted.
- Config: `tools.exec.host=gateway`, `tools.exec.security=allowlist`, `approvals.exec.enabled=true`
- If Dave is unavailable, `askFallback: "deny"` blocks the command.

### Discipline Files
- Email → `email.md` | Follow-ups → `follow-up.md` | Calendar → `calendar.md` | Comms → `communications.md`

### RingCentral
- **My Business Line:** (479) 319-3659 📱
- **Account:** Amber Ives (ext 420) - MindFire, Inc.
- **SMS Channel Plugin:** ✅ Working (first-class OpenClaw channel)
- **Team Messaging:** ✅ Working (first-class OpenClaw channel)
- **Auth:** JWT Bearer token (permanent, `.env-ringcentral`)

# TOOLS.md - Local Notes

Environment-specific config. Skills define how tools work; this is your cheat sheet.

### Zoom (Dave's PMI)
- Link: https://mindfire.zoom.us/j/4630269255?pwd=VE9McTZFRXlMV01MTEFweklnbDFWZz09
- Meeting ID: 463 026 9255 | Passcode: boom!
- Phone: +1 312-626-6799 (passcode 541630)

### Message Routing & Cross-Channel Continuity
- `sessions_send` → internal OpenClaw messages between sessions
- `message` tool → external platform messages (Telegram, Discord, etc.)
- Session visibility: `tools.sessions.visibility: "all"` enabled
- **Cross-channel continuity:** Dave's identity is linked across Telegram, RC SMS, and RC Team. All of Dave's DMs share session context. What he says on Telegram, you remember on SMS.
- **Memory is the backup:** Even if sessions reset, daily notes and `memory_search` provide continuity. Always search memory when context seems missing.

### Calendar Access
- Dave's calendar ID: `daver@mindfireinc.com` (shared to my account)
- List events: `gog cal events daver@mindfireinc.com --from X --to Y` (NOT `events ls`)
- Create events: `gog cal create daver@mindfireinc.com --summary ... --from ... --to ...`
- My calendar (aives@mindfiremail.info) has no primary events; always use Dave's ID

### Exec Approvals (Email Safety System) - ACTIVE

**Read operations (NO approval needed):**
- Email reads: Use `gog-email-read.sh gmail messages search ...` (allowlisted wrapper)
- Email thread reads: Use `gog-email-read.sh gmail thread get ...` (allowlisted wrapper)
- Calendar reads: Use `gog-cal-read.sh cal events ...` (allowlisted wrapper)
- These wrapper scripts ONLY permit read-only gog subcommands. They reject sends/creates.

**Write operations (approval REQUIRED):**
- Email sends: Use `gog gmail send ...` (requires Dave's Telegram approval)
- Email replies: Use `gog gmail reply ...` (requires Dave's Telegram approval)
- Calendar creates: Use `gog cal create ...` (requires Dave's Telegram approval)
- Thread modifications: Use `gog gmail thread modify ...` (requires Dave's Telegram approval)

**Approval mechanics:**
- Dave receives a prompt with full UUID, command details, and expiry
- Dave approves with `/approve <FULL-UUID> allow-once` (NEVER `allow-always` for gog)
- Always use `timeout: 3600` (60 min) so Dave has time to approve
- Cannot auto-send copy-paste approval lines (approval forwarding bypasses main session)
- If Dave is unavailable, `askFallback: "deny"` blocks the command

**Configuration:**
- `gog-email-read.sh` and `gog-cal-read.sh` should be on the exec allowlist
- Raw `gog` binary is NOT on the allowlist (all raw gog commands need approval)
- All other binaries in `/bin/*`, `/usr/bin/*`, `/usr/local/bin/*` (except gog) are allowlisted
- Config: `tools.exec.host=gateway`, `tools.exec.security=allowlist`, `approvals.exec.enabled=true`

**If wrapper scripts trigger on-miss (allowlist not working):**
- The wrappers enforce read-only safety even without the allowlist -- they reject send/reply commands
- If the approval prompt fires for a wrapper call, approve it -- it's safe (read-only)
- Use `allow-always` for the wrapper script paths specifically (NOT for raw gog)
- See `docs/RUNTIME-CONFIG.md` section 3 for troubleshooting steps
- Report the issue to Dave so Claude Code can diagnose the allowlist configuration

### Discipline Files
- Email → `email.md` | Follow-ups → `follow-up.md` | Calendar → `calendar.md` | Comms → `communications.md`

### RingCentral
- **My Business Line:** (479) 319-3659 📱
- **Account:** Amber Ives (ext 420) - MindFire, Inc.
- **SMS Channel Plugin:** ✅ Working (first-class OpenClaw channel)
- **Team Messaging:** ✅ Working (first-class OpenClaw channel)
- **Auth:** JWT Bearer token (permanent, `.env-ringcentral`)

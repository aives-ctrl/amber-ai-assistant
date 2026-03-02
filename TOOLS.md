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

### Discipline Files
- Email → `email.md` | Follow-ups → `follow-up.md` | Calendar → `calendar.md` | Comms → `communications.md`

### RingCentral
- **My Business Line:** (479) 319-3659 📱
- **Account:** Amber Ives (ext 420) - MindFire, Inc.
- **SMS Channel Plugin:** ✅ Working (first-class OpenClaw channel)
- **Team Messaging:** ✅ Working (cron-based, refactor to channel plugin pending)
- **Direct Chat with Dave:** Chat ID 1595320049666
- **Auth:** JWT Bearer token (permanent, `.env-ringcentral`)

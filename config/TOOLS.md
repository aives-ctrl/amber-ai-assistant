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

### Calendar Access -- see `skills/calendar-read/SKILL.md` and `skills/calendar-create/SKILL.md`
- Dave's calendar ID: `daver@mindfireinc.com` (shared to my account)
- List events: use calendar-read skill (wrapper script `/Users/amberives/.openclaw/workspace/scripts/gog-cal-read.sh`, no approval needed)
- Create events: use calendar-create skill (raw `gog`, approval required)
- My calendar (aives@mindfiremail.info) has no primary events; always use Dave's ID

### Skills (Canonical Patterns)

Skills define the exact commands and processes for common operations. Always follow the skill pattern instead of improvising exec commands.

| Skill | Location | Approval? |
|-------|----------|-----------|
| email-read | `skills/email-read/SKILL.md` | NO - allowlisted wrapper |
| email-send | `skills/email-send/SKILL.md` | YES - draft first, then approve |
| calendar-read | `skills/calendar-read/SKILL.md` | NO - allowlisted wrapper |
| calendar-create | `skills/calendar-create/SKILL.md` | YES - propose to Dave first |
| startup | `skills/startup/SKILL.md` | NO - run at every session start |

### Verification Sub-Agent (Opus 4.6)

**Pattern:** Before any irreversible action, call Opus to check your parameters. Opus costs fractions of a cent per call and catches mistakes you keep making.

| Script | Purpose |
|--------|---------|
| `scripts/verify-with-opus.sh` | General Opus verification — pass a prompt template + variables |
| `scripts/verify-email-params.sh` | Bash fallback — regex checks if Opus/Gateway is down |

**Prompt templates** live in `config/verify-prompts/`. Each domain gets its own:
| Template | File | Checks |
|----------|------|--------|
| email-send | `config/verify-prompts/email-send.md` | Threading, reply-all, HTML format, signature, CC, subject |

**How it works:**
1. You build your action parameters (e.g., the gog send command)
2. Call `verify-with-opus.sh <template> --var key=value ...`
3. Opus returns `{approved: true/false, errors: [...], summary: "..."}`
4. If approved → execute the action
5. If not → fix errors, re-verify

**To add a new domain:** Create `config/verify-prompts/<domain>.md` with `{{variable}}` placeholders. Then call `verify-with-opus.sh <domain> --var key=value ...`

### Workflows (Multi-Step Pipelines — FUTURE)

| Workflow | Location | Status |
|----------|----------|--------|
| email-triage | `workflows/email-triage.lobster` | Not yet operational (lobster registration TBD) |
| email-send | `workflows/email-send.lobster` | Not yet operational — using direct gog send + verify instead |

### Exec Approvals (Email Safety System) - ACTIVE

**How it works:**
- **Read/tag commands** use allowlisted wrapper scripts (full path). These are pre-approved — no exec approval needed.
- **Write commands** (`gog gmail send`, `gog cal create`) use bare `gog` → they trigger exec-approval via Dave's Telegram.
- Basic shell tools (grep, cat, ls) are allowlisted. They don't trigger approval.
- Approval prompts go to Dave's PRIVATE Telegram chat. Amber cannot self-approve.

**Read operations (NO approval needed) — use wrapper scripts:**
- Email reads: `/Users/amberives/.openclaw/workspace/scripts/gog-email-read.sh gmail messages search ...`
- Calendar reads: `/Users/amberives/.openclaw/workspace/scripts/gog-cal-read.sh cal events ...`
- **NEVER use bare `gog` for reads** — it will trigger unnecessary approval.
- Run ONE command at a time. No parallel reads.

**Write operations (approval REQUIRED) — use bare `gog`:**
- Email sends: `gog gmail send ...` (Dave approves via Telegram buttons)
- Email replies: `gog gmail send --reply-to-message-id ...` (Dave approves)
- Calendar creates: `gog cal create ...` (Dave approves)
- ONE command at a time. Wait for approval before next command.

**Thread tagging (NO approval needed) — use wrapper script:**
- `/Users/amberives/.openclaw/workspace/scripts/gog-email-tag.sh gmail thread modify <threadId> --add "Handled" ...`

**Self-approval is impossible and forbidden.** Approvals route to Dave's private chat. See AGENTS.md.

### Git Sync (Preserving Your Memory)
- **You MUST commit and push after editing memory files.** See AGENTS.md "Git Sync" section.
- `update-self.sh` auto-syncs before pulling, but don't rely on that alone — push after significant edits.
- Sync command: `cd /Users/amberives/amber-ai-assistant && git add memory/ config/follow-up-tracker.md && git commit -m "Amber: sync local changes" && git push origin main`
- **If you skip this, your changes WILL be overwritten on the next pull.**

### Discipline Files
- Email → `email.md` | Follow-ups → `follow-up.md` | Calendar → `calendar.md` | Comms → `communications.md`

### RingCentral
- **My Business Line:** (479) 319-3659 📱
- **Account:** Amber Ives (ext 420) - MindFire, Inc.
- **SMS Channel Plugin:** ✅ Working (first-class OpenClaw channel)
- **Team Messaging:** ✅ Working (first-class OpenClaw channel)
- **Auth:** JWT Bearer token (permanent, `.env-ringcentral`)

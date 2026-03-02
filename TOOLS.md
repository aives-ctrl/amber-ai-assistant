# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

### Zoom (Dave's PMI)

- Link: https://mindfire.zoom.us/j/4630269255?pwd=VE9McTZFRXlMV01MTEFweklnbDFWZz09
- Meeting ID: 463 026 9255
- Passcode: boom!
- Phone: +1 312-626-6799 (passcode 541630)

## Cross-Session Coordination

**Configuration:** `tools.sessions.visibility: "all"` enabled in OpenClaw config
- Allows monitoring group chats from DM sessions using `sessions_history`
- Essential for multi-context experiments requiring private guidance + group interaction

**Message Routing:**
- `sessions_send` → Internal OpenClaw messages between sessions
- `message` tool → External platform messages (Telegram, Discord, etc.)

## Telegram Group Chat Configuration

**Key settings learned (March 1, 2026):**
- `groupPolicy: "open"` — allows all senders in groups (default "allowlist" blocks everyone if no `groupAllowFrom` set)
- `requireMention: false` — must be false to see ALL group messages (true = only @mentions processed)
- Group chat ID for "David, Amber Ives and Ryan": `-5203397190`
- Group session key: `agent:main:telegram:group:-5203397190`

**Common pitfalls:**
- `groupPolicy: "allowlist"` without `groupAllowFrom` = ALL group messages blocked silently
- `requireMention: true` = only @mentioned messages reach agent; everything else invisible
- Gateway must be restarted after config changes (ask user to run `openclaw gateway restart`)
- Never `kill -9` the gateway — ask user to restart manually

## Discipline-Specific Rules

- **Email handling:** See `email.md` for all email rules, formatting, threading, and processing
- **Follow-up tracking:** See `follow-up.md` for timing rules, tracking system, and processes  
- **Calendar & meetings:** See `calendar.md` for scheduling, coordination, and meeting processes
- **Communications:** See `communications.md` for messaging, reactions, and platform behavior

## Notification Priority Queue

**Default routing:** All outbound notifications should go through the queue to prevent notification fatigue.

**Usage:**
- `./scripts/notify "message" --tier critical` - Immediate delivery
- `./scripts/notify "message" --tier high` - Batched hourly  
- `./scripts/notify "message" --tier medium` - Batched every 3 hours
- `./scripts/notify "message" --bypass` - Skip queue, send immediately

**Automatic classification:** If no tier specified, messages are auto-classified based on keywords and source.

**Batch delivery:**
- High priority: Every hour at :00
- Medium priority: Every 3 hours (12am, 3am, 6am, 9am, 12pm, 3pm, 6pm, 9pm)
- Critical: Always immediate

**Queue management:**
- `./scripts/notification-queue.py status` - Show queue status
- `./scripts/notification-queue.py flush high` - Manual flush high priority
- `./scripts/notification-queue.py flush medium` - Manual flush medium priority

## SMS/Phone System  

### 🚀 ACTIVE: RingCentral (Enterprise Solution) ✅ WORKING!
- **My Business Line:** (479) 319-3659 📱
- **Account:** Amber Ives (ext 420) - MindFire, Inc.
- **API Status:** ✅ Authenticated via JWT (never expires)
- **Team Messaging:** ✅ Reading and sending messages working!
- **Direct Chat with Dave:** Chat ID 1595320049666
- **SMS:** ⏳ Pending TCR registration (72hrs to weeks)
- **Credentials:** `.env-ringcentral` (secured, chmod 600)
- **Auth method:** JWT Bearer token (RingCentral-generated, permanent)

### 🚫 Google Voice (Deactivated)
- **Previous number:** 949-264-BREW (949-264-2739) 🍺  
- **Status:** ❌ Deactivated - replaced by professional RingCentral system
- **Why removed:** Broken libraries, token-heavy browser automation, consumer-grade service
- **Replaced by:** Enterprise RingCentral solution

### 🎯 Migration Plan
1. **Get RingCentral credentials** from Dave's business account
2. **Test RingCentral integration** with new phone number  
3. **Switch to RingCentral** for both sending and receiving
4. **Result:** 99% token reduction + enterprise reliability

Add whatever helps you do your job. This is your cheat sheet.

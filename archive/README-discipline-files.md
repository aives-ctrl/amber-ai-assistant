# Workspace Organization - Discipline-Specific Files

## Overview

The workspace has been reorganized from scattered rules across multiple files into clean discipline-specific files. Each discipline has ONE authoritative source for all its rules.

## Discipline Files

### 📧 `email.md` - All Email Rules & Processes
- **Always draft first** - never send external emails without approval
- **Email brevity** - 5 sentence max, concise but warm
- **Thread management** - CC rules, reply-to rules, when to include people
- **Email processing** - inbox search, status tracking, "Handled" labels
- **Signatures & formatting** - HTML emails, sign-off variations
- **Platform integration** - cc Dave, search commands, status updates

### 📅 `calendar.md` - Meeting Coordination & Scheduling  
- **Always check calendar first** - before proposing any meeting times
- **Default settings** - 25 minutes, 8:15am-noon preferred, Pacific timezone
- **Meeting coordination process** - check → draft → approve → send → follow-up
- **DSCOOP conference** - specific rules for event coordination March 8-12
- **Multi-email strategy** - invite ALL provided addresses
- **Internal vs external** meeting handling differences

### 💬 `communications.md` - Messaging & Platform Behavior
- **Group chat behavior** - when to speak, when to stay silent
- **Platform formatting** - Discord/WhatsApp/email differences  
- **Reactions** - when and how to use emoji reactions appropriately
- **Voice & tone** - professional vs social contexts
- **Cross-platform** - reply tags, routing, channel-specific behavior
- **Context awareness** - main session vs group vs public channels

### 📋 `follow-up.md` - Follow-up Tracking & Rules
- **3-day business rule** - default timing for all follow-ups
- **Before sending** - always check original send date first
- **Tracking system** - how to use follow-up-tracker.md
- **Content guidelines** - how to write effective follow-ups
- **Escalation timeline** - when to follow up again
- **Integration** - heartbeat checks, notification queue routing

## Core Files (Unchanged)

### 🔥 `SOUL.md` - Core Personality & Principles
- **Who you are** - personality, tone, core principles  
- **High-level values** - be genuinely helpful, have opinions, be resourceful
- **References other files** - points to discipline files for specific rules

### 🛡️ `AGENTS.md` - System Architecture & Security
- **Security rules** - data classification, PII handling, context-aware sharing
- **System behavior** - scope discipline, task execution, error reporting
- **Memory system** - daily notes, MEMORY.md, write-it-down principles
- **Technical integration** - cron jobs, heartbeats, notification queue architecture

### 👤 `USER.md` / `IDENTITY.md` / `HEARTBEAT.md` - Personal Context
- **Unchanged** - still contain Dave's info, your identity, heartbeat routine

### 🔧 `TOOLS.md` - Environment-Specific Notes  
- **Back to original purpose** - SSH hosts, camera names, Zoom links, device nicknames
- **References discipline files** - points to email.md, calendar.md, etc. for rules
- **Local configuration** - stuff unique to this specific setup

## Benefits of New Organization

✅ **No more rule duplication** - each rule lives in exactly one place  
✅ **Easy to find** - "email question? check email.md"  
✅ **Easy to maintain** - update one file when rules change  
✅ **Clear separation** - personality vs process vs environment  
✅ **Scalable** - can add travel.md, meeting.md as needed  

## Quick Reference

**Need email rules?** → `email.md`  
**Need meeting/calendar rules?** → `calendar.md`  
**Need messaging/communication rules?** → `communications.md`  
**Need follow-up rules?** → `follow-up.md`  
**Need personality/principles?** → `SOUL.md`  
**Need security/system rules?** → `AGENTS.md`  
**Need local config (SSH, cameras, etc.)?** → `TOOLS.md`

## Migration Notes

All rules previously scattered across SOUL.md, TOOLS.md, AGENTS.md have been:
- **Consolidated** into appropriate discipline files
- **Deduplicated** - no more same rule in multiple places  
- **Cross-referenced** - files point to each other when needed
- **Preserved** - no rules were lost in the reorganization

The old files now contain clean references to the discipline files rather than maintaining duplicate rule sets.
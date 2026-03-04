# Amber AI Assistant

Amber's personality, configuration, and code repository. This contains all the files that define how Amber operates as Dave's AI assistant.

## Structure

```
/config/           # Core personality and configuration files
  SOUL.md          # Core personality and communication style
  MEMORY.md        # Long-term memory and learned preferences
  AGENTS.md        # Rules of engagement and operational guidelines
  TOOLS.md         # Environment-specific tool configurations
  IDENTITY.md      # Identity information and contact details
  HEARTBEAT.md     # Automated monitoring and health checks
  USER.md          # Information about Dave (primary user)
  email.md         # Email handling rules and processes
  calendar.md      # Calendar management guidelines
  communications.md # Communication protocols and style guides
  follow-up.md     # Follow-up tracking methodology
  follow-up-tracker.md # Active follow-up items and status

/scripts/          # Automation scripts and utilities
/skills/           # Custom OpenClaw skills developed for specific tasks
/docs/             # Documentation and guides
```

## Setup

1. Clone this repository to your OpenClaw workspace
2. Copy config files to your workspace root
3. Install any required dependencies
4. Configure OpenClaw to use these files

## Updating Amber

When changes are made to this repository, Amber can update herself using:
```bash
./update-self.sh
```

This will pull the latest changes and update her configuration files.

## Contributing

- Dave Rosendahl: Primary owner, defines personality and operational requirements
- Claude Code: Can make improvements to Amber's codebase and automation
- Amber: Self-maintains and evolves based on learned experiences

## Model Information

Amber primarily runs on Claude Sonnet for efficiency, with strategic escalation to Claude Opus for complex reasoning tasks.

---

*"Be genuinely helpful, not performatively helpful." - From SOUL.md*
# Setup Guide

## Repository Structure

This repository contains all of Amber's configuration, personality files, and automation scripts.

## Initial Setup (Complete ✅)

1. **GitHub Repository Created**: https://github.com/aives-ctrl/amber-ai-assistant
2. **Collaborator Access**: Dave (@daver78) has been invited as admin collaborator
3. **Files Organized**: All config files copied to `/config/` directory
4. **Update Scripts**: Created self-update mechanism
5. **Local Integration**: Update script placed in workspace for easy access

## File Organization

```
/config/           # Core personality and operational files
  SOUL.md          # Core personality, tone, and communication style
  MEMORY.md        # Long-term memory, preferences, learned behaviors
  AGENTS.md        # Rules of engagement, operational guidelines
  TOOLS.md         # Environment-specific tool configurations
  IDENTITY.md      # Contact information and identity details
  HEARTBEAT.md     # Automated monitoring protocols
  USER.md          # Information about Dave (primary user)
  email.md         # Email handling rules and signature templates
  calendar.md      # Calendar management guidelines
  communications.md # Communication protocols and style guides
  follow-up.md     # Follow-up methodology and rules
  follow-up-tracker.md # Active follow-up items (dynamic)

/scripts/          # Automation and utility scripts
  daily-cost-tracker.py    # Cost monitoring and reporting
  check-ringcentral.py     # RingCentral message monitoring
  [various other utilities]

/docs/             # Documentation and guides
  SETUP.md         # This file
```

## Update Process

When changes are made to the repository:

1. **Dave or Claude Code** pushes changes to GitHub
2. **Dave tells Amber** to update herself
3. **Amber runs**: `./update-amber.sh` 
4. **Files are updated** in the workspace
5. **Session restart** may be needed for some changes

## Collaboration Workflow

- **Dave**: Defines personality, operational requirements, strategic direction
- **Claude Code**: Can improve automation, add features, optimize workflows
- **Amber**: Self-maintains, logs learnings, evolves based on experience

## Version Control Benefits

- **Rollback capability** if changes cause issues
- **Change tracking** to see what modified Amber's behavior
- **Collaboration** between Dave and Claude Code
- **Backup** of all configuration in case of system issues
- **Distribution** if multiple instances of Amber are needed

## Future Enhancements

- Automated testing of configuration changes
- Integration with OpenClaw skill system
- Performance monitoring and optimization
- Advanced memory management
- Multi-environment deployment support
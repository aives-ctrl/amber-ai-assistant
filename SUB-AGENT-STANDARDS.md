# Sub-Agent Standards & Organization

Every OpenClaw sub-agent must maintain its own development tracking and accountability.

## Required Files Per Agent

### SKILL.md  
- Core functionality and instructions
- Process workflows and decision trees
- Tool usage and API integration
- Error handling and fallback procedures

### CHANGELOG.md
- **Agent self-maintains:** All modifications made, when, and why
- **Version tracking:** Major changes, architecture decisions  
- **Historical record:** What worked, what didn't, lessons learned
- **Format:** Reverse chronological (newest first)

### BACKLOG.md  
- **Agent self-maintains:** Features to add, improvements needed
- **Priority levels:** High/Medium/Low with business justification
- **Completed features:** Track what's been implemented
- **Rejected features:** What won't be built and why

## Agent Responsibility
Each sub-agent is responsible for:
- ✅ **Updating CHANGELOG.md** when modifications are made
- ✅ **Managing BACKLOG.md** with feature requests and priorities  
- ✅ **Self-documenting** changes and decisions
- ✅ **Tracking completions** and moving items from backlog to completed

## Benefits
- **Clear ownership:** Each agent owns its development roadmap
- **No lost features:** Requests tracked in appropriate backlog
- **Historical context:** Why changes were made and what was learned
- **Development accountability:** Agents maintain their own standards

## Standards for New Agents
When creating new sub-agents:
1. **Create SKILL.md** with core functionality
2. **Initialize CHANGELOG.md** with v1.0 creation entry
3. **Initialize BACKLOG.md** with known feature requirements
4. **Document architecture decisions** in changelog
5. **Set up maintenance process** for ongoing updates

## Example Structure
```
skills/
├── agent-name/
│   ├── SKILL.md         # Core functionality 
│   ├── CHANGELOG.md     # What changed, when, why
│   ├── BACKLOG.md       # What's planned, priorities
│   └── [other files]    # Scripts, configs, data
```

This ensures every sub-agent has clear development tracking and accountability for its own evolution.
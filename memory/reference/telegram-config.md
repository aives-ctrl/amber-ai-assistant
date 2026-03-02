# Telegram Group Chat Configuration

**Key settings (March 1, 2026):**
- `groupPolicy: "open"` — allows all senders in groups
- `requireMention: false` — must be false to see ALL group messages
- Group chat ID for "David, Amber Ives and Ryan": `-5203397190`
- Group session key: `agent:main:telegram:group:-5203397190`

**Common pitfalls:**
- `groupPolicy: "allowlist"` without `groupAllowFrom` = ALL group messages blocked silently
- `requireMention: true` = only @mentioned messages reach agent
- Gateway must be restarted after config changes

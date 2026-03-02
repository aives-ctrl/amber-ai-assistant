# Cross-Session Coordination

For experiments requiring coordination between multiple chat contexts:

1. Set session visibility: `tools.sessions.visibility: "all"` in OpenClaw config
2. Use `sessions_history` to monitor other session conversations  
3. Use `message` tool to send actual platform messages (not `sessions_send`)
4. Use `sessions_send` only for internal OpenClaw coordination between sessions

Key distinction: `sessions_send` = internal OpenClaw messages, `message` = external platform messages.

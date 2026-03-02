# RingCentral Processor - Feature Backlog

## High Priority
- **🔥 More frequent checking:** 5 minutes too long for real-time team messaging (Dave request 2026-03-01)
  - Options: 30 seconds, 1 minute with rate limit handling, or real-time WebSocket
  - Need to solve rate limiting issues for frequent polling
- **Group chat support:** Expand beyond direct chat with Dave to team channels
- **Message threading:** Better context for ongoing conversations in group chats

## Medium Priority
- **Smart notifications:** Only announce important messages, suppress routine chatter
- **Team member recognition:** Identify and track different team members in conversations  
- **Response prioritization:** Urgent vs routine message detection for faster response
- **Offline message queuing:** Handle messages that arrive when system is down

## Low Priority
- **Message search:** Search conversation history across all RingCentral chats
- **Analytics:** Track team communication patterns and response times
- **Integration with phone/video:** Handle RingCentral calls and video meetings
- **File sharing support:** Process document shares and attachments in team messages

## Completed Features
- ✅ OpenClaw sub-agent architecture  
- ✅ Direct chat message processing
- ✅ Full business context and tool access
- ✅ Conversation history logging
- ✅ Rate limit error handling

## Rejected/Won't Do
- WebSocket real-time (abandoned due to permission/notification issues)
- Standalone polling script (migrated to OpenClaw architecture)
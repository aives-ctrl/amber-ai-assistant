# RingCentral Integration 🔥

## Status: PRODUCTION READY ✅

Clean, simple RingCentral integration with notifications and on-demand responses.

## Features

- **⚡ Instant notifications** - WebSocket push, not polling
- **🔔 Critical priority** - immediate delivery via notification queue  
- **🔄 Auto-reconnection** - handles network drops gracefully
- **📱 Smart filtering** - only notifies about Dave's messages to me
- **🛡️ Error recovery** - robust error handling and retry logic

## Service Management

```bash
# Check status
/Users/amberives/.openclaw/workspace/scripts/ringcentral-service.sh status

# Start service
/Users/amberives/.openclaw/workspace/scripts/ringcentral-service.sh start

# Stop service  
/Users/amberives/.openclaw/workspace/scripts/ringcentral-service.sh stop

# Restart service
/Users/amberives/.openclaw/workspace/scripts/ringcentral-service.sh restart

# View real-time logs
/Users/amberives/.openclaw/workspace/scripts/ringcentral-service.sh logs
```

## Testing

**Send Dave a RingCentral message** - you should get an **instant critical priority notification!**

## Implementation Details

- **WebSocket Protocol**: Authenticated secure WebSocket with RingCentral
- **Event Filter**: `/restapi/v1.0/glip/posts` (all message events)
- **Chat Filter**: Only messages in direct chat ID `1595320049666`
- **Notification Tier**: `critical` for instant delivery
- **Log Location**: `/tmp/ringcentral-realtime.log`
- **PID File**: `/Users/amberives/.openclaw/workspace/ringcentral-realtime.pid`

## Advantages over Polling

| Feature | Polling (Old) | Real-time WebSocket (New) |
|---------|---------------|---------------------------|
| **Response Time** | 5-10 minutes | **Instant** |
| **Resource Usage** | Periodic API calls | Persistent connection |
| **Reliability** | High | **Very High** |
| **Notification Priority** | High | **Critical** |
| **Network Efficiency** | Good | **Excellent** |

## Troubleshooting

1. **Service not starting**: Check credentials in `.env-ringcentral`
2. **No notifications**: Verify direct chat ID `1595320049666`  
3. **Connection issues**: Check logs with `ringcentral-service.sh logs`
4. **WebSocket errors**: Service auto-reconnects with exponential backoff

## Migration Complete

- ❌ **Old**: 5-minute polling via LaunchAgent → **REMOVED**
- ✅ **New**: Instant WebSocket notifications → **ACTIVE**

**The real-time system is now the primary RingCentral notification method.**
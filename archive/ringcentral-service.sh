#!/bin/bash
# RingCentral Real-time Service Management Script

WORKSPACE="/Users/amberives/.openclaw/workspace"
SCRIPT="$WORKSPACE/scripts/ringcentral-hybrid.py"
PIDFILE="$WORKSPACE/ringcentral-realtime.pid"
LOGFILE="/tmp/ringcentral-realtime.log"

case "$1" in
    start)
        if [ -f "$PIDFILE" ] && kill -0 "$(cat $PIDFILE)" 2>/dev/null; then
            echo "🔥 RingCentral real-time is already running (PID: $(cat $PIDFILE))"
            exit 1
        fi
        
        echo "🚀 Starting RingCentral real-time notifications..."
        cd "$WORKSPACE"
        source sms-env/bin/activate
        nohup python "$SCRIPT" > "$LOGFILE" 2>&1 &
        echo $! > "$PIDFILE"
        echo "✅ Started with PID $(cat $PIDFILE)"
        echo "📋 Logs: tail -f $LOGFILE"
        ;;
        
    stop)
        if [ -f "$PIDFILE" ]; then
            PID=$(cat "$PIDFILE")
            if kill -0 "$PID" 2>/dev/null; then
                kill "$PID"
                rm -f "$PIDFILE"
                echo "👋 Stopped RingCentral real-time service (PID: $PID)"
            else
                echo "⚠️ Process not running, cleaning up PID file"
                rm -f "$PIDFILE"
            fi
        else
            echo "❌ No PID file found - service not running"
        fi
        ;;
        
    restart)
        $0 stop
        sleep 2
        $0 start
        ;;
        
    status)
        if [ -f "$PIDFILE" ] && kill -0 "$(cat $PIDFILE)" 2>/dev/null; then
            PID=$(cat "$PIDFILE")
            echo "✅ RingCentral real-time is running (PID: $PID)"
            echo "📋 Log file: $LOGFILE"
            if [ -f "$LOGFILE" ]; then
                echo "📊 Last 5 log lines:"
                tail -5 "$LOGFILE"
            fi
        else
            echo "❌ RingCentral real-time is not running"
            if [ -f "$PIDFILE" ]; then
                rm -f "$PIDFILE"
            fi
        fi
        ;;
        
    logs)
        if [ -f "$LOGFILE" ]; then
            tail -f "$LOGFILE"
        else
            echo "❌ Log file not found: $LOGFILE"
        fi
        ;;
        
    *)
        echo "🔥 RingCentral Real-time Service Manager"
        echo "Usage: $0 {start|stop|restart|status|logs}"
        echo ""
        echo "Commands:"
        echo "  start   - Start real-time notifications"
        echo "  stop    - Stop real-time notifications" 
        echo "  restart - Restart the service"
        echo "  status  - Check if service is running"
        echo "  logs    - Follow the logs in real-time"
        exit 1
        ;;
esac

exit 0
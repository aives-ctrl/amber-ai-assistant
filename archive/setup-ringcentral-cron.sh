#!/bin/bash
# Setup cron job for RingCentral message monitoring (every 10 minutes)

CRON_LINE="*/10 * * * * cd /Users/amberives/.openclaw/workspace && source sms-env/bin/activate && python scripts/ringcentral-monitor.py >> /tmp/ringcentral-monitor.log 2>&1"

# Add to crontab
(crontab -l 2>/dev/null; echo "$CRON_LINE") | crontab -

echo "✅ RingCentral monitoring cron job added - checking every 10 minutes"
echo "   Logs: /tmp/ringcentral-monitor.log"
echo "   To remove: crontab -l | grep -v ringcentral-monitor | crontab -"
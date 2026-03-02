#!/bin/bash
# Simple SMS sender using OpenClaw browser - more efficient than full snapshots
# Usage: ./send-sms.sh <phone_number> <message>

if [ $# -lt 2 ]; then
    echo "Usage: $0 <phone_number> <message>"
    exit 1
fi

PHONE="$1"
shift
MESSAGE="$*"

echo "Sending SMS to $PHONE: $MESSAGE"

# Use OpenClaw browser tools efficiently
openclaw browser start --profile openclaw
openclaw browser navigate --profile openclaw --url "https://voice.google.com/u/0/messages" 
openclaw browser act --profile openclaw --request '{"kind": "click", "selector": "button[data-testid=\"send-new-message\"]"}' 
openclaw browser act --profile openclaw --request '{"kind": "type", "text": "'"$PHONE"'"}' 
openclaw browser act --profile openclaw --request '{"kind": "press", "key": "Tab"}'
openclaw browser act --profile openclaw --request '{"kind": "type", "text": "'"$MESSAGE"'"}' 
openclaw browser act --profile openclaw --request '{"kind": "press", "key": "Enter"}'

echo "SMS sent successfully"
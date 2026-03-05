#!/bin/bash

# gog-cal-read.sh -- Allowlisted wrapper for READ-ONLY calendar operations
# This script is on the exec allowlist. It ONLY runs safe, read-only gog commands.
# gog cal create/update MUST go through raw gog (requires exec approval).
#
# Usage: gog-cal-read.sh cal events daver@mindfireinc.com --from X --to Y
#        gog-cal-read.sh cal get daver@mindfireinc.com <eventId>

CMD="$*"

# Allowlist of read-only subcommands
ALLOWED_PATTERNS=(
    "cal events"
    "cal get"
    "cal list"
)

# Check if the command matches an allowed pattern
ALLOWED=false
for pattern in "${ALLOWED_PATTERNS[@]}"; do
    if [[ "$CMD" == *"$pattern"* ]]; then
        ALLOWED=true
        break
    fi
done

if [ "$ALLOWED" = true ]; then
    exec /Users/amberives/.openclaw/workspace/scripts/gog-real $CMD
else
    echo "ERROR: This wrapper only allows read-only calendar operations."
    echo "Allowed: cal events, cal get, cal list"
    echo "For cal create/update operations, use 'gog' directly (requires Dave's approval)."
    exit 1
fi

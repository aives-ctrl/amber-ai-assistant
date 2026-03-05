#!/bin/bash

# gog-email-read.sh -- Allowlisted wrapper for READ-ONLY email operations
# This script is on the exec allowlist. It ONLY runs safe, read-only gog commands.
# gog gmail send/reply MUST go through raw gog (requires exec approval).
#
# Usage: gog-email-read.sh gmail messages search 'is:unread' --max 10
#        gog-email-read.sh gmail thread get <threadId>
#        gog-email-read.sh gmail labels list

CMD="$*"

# Allowlist of read-only subcommands (both singular and plural forms)
ALLOWED_PATTERNS=(
    "gmail messages search"
    "gmail message search"
    "gmail messages get"
    "gmail message get"
    "gmail messages list"
    "gmail message list"
    "gmail threads get"
    "gmail thread get"
    "gmail threads list"
    "gmail thread list"
    "gmail labels list"
    "gmail labels get"
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
    exec gog $CMD
else
    echo "ERROR: This wrapper only allows read-only email operations."
    echo "Allowed: gmail messages search, gmail messages get, gmail thread get/list, gmail labels list"
    echo "For send/reply operations, use 'gog' directly (requires Dave's approval)."
    exit 1
fi

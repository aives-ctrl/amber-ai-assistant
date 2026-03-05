#!/bin/bash

# gog-email-tag.sh -- Allowlisted wrapper for email TAGGING operations
# This script is on the exec allowlist. It ONLY runs safe thread-labeling commands.
# gog gmail send/reply MUST go through raw gog (requires exec approval).
#
# Usage: gog-email-tag.sh gmail thread modify <threadId> --add "Handled" --remove "UNREAD" --force
#        gog-email-tag.sh gmail thread modify <threadId> --add "Handled" --force
#        gog-email-tag.sh gmail thread modify <threadId> --remove "UNREAD" --force

CMD="$*"

# Allowlist: only gmail thread modify (label management) — both singular and plural
ALLOWED_PATTERNS=(
    "gmail thread modify"
    "gmail threads modify"
)

# Blocklist: reject anything that could send, delete, or trash
BLOCKED_PATTERNS=(
    "gmail send"
    "gmail reply"
    "gmail draft"
    "gmail messages delete"
    "gmail messages trash"
    "gmail thread delete"
    "gmail thread trash"
)

# Check blocklist first (safety)
for pattern in "${BLOCKED_PATTERNS[@]}"; do
    if [[ "$CMD" == *"$pattern"* ]]; then
        echo "ERROR: This wrapper does NOT allow destructive or send operations."
        echo "Blocked: $pattern"
        echo "For send/reply operations, use 'gog' directly (requires Dave's approval)."
        exit 1
    fi
done

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
    echo "ERROR: This wrapper only allows email tagging (thread modify) operations."
    echo "Allowed: gmail thread modify <threadId> --add/--remove <label>"
    echo "For send/reply operations, use 'gog' directly (requires Dave's approval)."
    exit 1
fi

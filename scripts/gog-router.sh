#!/bin/bash

# gog-router.sh -- Shadow wrapper that intercepts ALL gog calls
#
# PURPOSE: Amber's agent sometimes calls raw `gog` instead of the wrapper scripts,
# despite instructions in 4+ config files. This is a known OpenClaw community issue --
# prompt-level enforcement is unreliable. This script provides STRUCTURAL enforcement.
#
# HOW IT WORKS:
# 1. Installed at /Users/amberives/.openclaw/bin-overrides/gog
# 2. openclaw.json has pathPrepend: ["/Users/amberives/.openclaw/bin-overrides"]
# 3. When Amber runs `gog <anything>`, this script intercepts it FIRST
# 4. Read-only email ops → routed to gog-email-read.sh (no approval needed)
# 5. Read-only calendar ops → routed to gog-cal-read.sh (no approval needed)
# 6. Thread tagging → routed to gog-email-tag.sh (no approval needed)
# 7. Everything else (send, reply, create) → passed to real gog (triggers approval)
#
# SAFETY: Send/reply/create operations are NOT intercepted. They pass through to
# the real gog binary at /usr/local/bin/gog, which still requires Dave's approval.

CMD="$*"
SCRIPTS_DIR="/Users/amberives/.openclaw/workspace/scripts"
REAL_GOG="/usr/local/bin/gog"

# --- Route read-only email operations to gog-email-read.sh ---
EMAIL_READ_PATTERNS=(
    "gmail messages search"
    "gmail messages get"
    "gmail thread get"
    "gmail thread list"
    "gmail labels list"
)

for pattern in "${EMAIL_READ_PATTERNS[@]}"; do
    if [[ "$CMD" == *"$pattern"* ]]; then
        exec "$SCRIPTS_DIR/gog-email-read.sh" $CMD
    fi
done

# --- Route read-only calendar operations to gog-cal-read.sh ---
CAL_READ_PATTERNS=(
    "cal events"
    "cal get"
    "cal list"
)

for pattern in "${CAL_READ_PATTERNS[@]}"; do
    if [[ "$CMD" == *"$pattern"* ]]; then
        exec "$SCRIPTS_DIR/gog-cal-read.sh" $CMD
    fi
done

# --- Route thread tagging to gog-email-tag.sh ---
if [[ "$CMD" == *"gmail thread modify"* ]]; then
    exec "$SCRIPTS_DIR/gog-email-tag.sh" $CMD
fi

# --- Everything else: pass through to real gog (requires approval) ---
# This includes: gmail send, gmail reply, gmail draft, cal create, cal update, etc.
exec "$REAL_GOG" $CMD

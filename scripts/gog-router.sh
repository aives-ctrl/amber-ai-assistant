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
# 7. Send/reply/create → BLOCKED with error message directing to /usr/local/bin/gog
#
# SECURITY NOTE: This router is trusted (in safeBinTrustedDirs), so it runs without
# exec-approval. If we passed sends through to real gog via `exec`, they would ALSO
# bypass approval (exec replaces the process inside the already-approved subprocess).
# Therefore sends MUST be blocked here, forcing Amber to call /usr/local/bin/gog
# explicitly, which IS subject to exec-approval.

CMD="$*"
SCRIPTS_DIR="/Users/amberives/.openclaw/workspace/scripts"

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

# --- BLOCK everything else (sends, creates, etc.) ---
# These operations require Dave's approval. Since this router is trusted,
# we CANNOT pass through to real gog (it would bypass approval).
# Instead, block and direct Amber to use the real binary path explicitly.
echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  BLOCKED: This command requires Dave's approval."
echo "  Use the full path to the real gog binary:"
echo ""
echo "  /usr/local/bin/gog $CMD"
echo ""
echo "  The approval system only works with /usr/local/bin/gog."
echo "═══════════════════════════════════════════════════════════"
echo ""
exit 1

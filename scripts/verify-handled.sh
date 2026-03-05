#!/bin/bash

# verify-handled.sh — Audit script to catch threads tagged "Handled"
# where no reply was sent by Amber (aives@mindfiremail.info).
#
# Checks threads labeled "Handled" from the last N hours against
# Amber's sent mail. Flags any thread that was tagged Handled but
# has no corresponding sent message from Amber in that thread.
#
# Usage:
#   ./verify-handled.sh              # Check last 24 hours
#   ./verify-handled.sh 48           # Check last 48 hours
#
# NOTE: This catches threads where Amber tagged Handled without
# replying. It's expected that some threads (FYI, automated emails)
# won't have replies — those are flagged but may be legitimate.
#
# Requires: gog-real binary in the same scripts directory.

REAL_GOG="$(dirname "$0")/gog-real"
HOURS="${1:-24}"

if [ ! -x "$REAL_GOG" ]; then
    echo "ERROR: gog-real not found at $REAL_GOG"
    echo "Run: cp /usr/local/bin/gog $(dirname "$0")/gog-real"
    exit 1
fi

echo "=== Handled Thread Audit (last ${HOURS}h) ==="
echo ""

# Get threads with Handled label (recent)
HANDLED_THREADS=$("$REAL_GOG" gmail threads list --label "Handled" --max 50 2>/dev/null)

if [ -z "$HANDLED_THREADS" ]; then
    echo "No threads with Handled label found."
    exit 0
fi

# Get sent messages from Amber in the same period
SENT_THREADS=$("$REAL_GOG" gmail messages search "from:aives@mindfiremail.info in:sent newer_than:${HOURS}h" --max 100 2>/dev/null)

echo "Threads labeled 'Handled': checking for sent replies..."
echo ""

# This is a basic audit — it prints Handled threads so you can
# visually check if they have corresponding sent messages.
# A full cross-reference would require parsing JSON output from gog.

echo "--- Handled threads (review for missing replies) ---"
echo "$HANDLED_THREADS" | head -30
echo ""
echo "--- Amber's sent messages (last ${HOURS}h) ---"
echo "$SENT_THREADS" | head -30
echo ""
echo "Compare the lists above. Any Handled thread without a"
echo "corresponding sent message may have been tagged prematurely."
echo ""
echo "Known exceptions (OK to tag without reply):"
echo "  - Automated/system emails"
echo "  - Mass newsletters"
echo "  - CC'd threads where no one addressed Amber"
echo "  - Threads flagged to Dave (action is 'flag', not 'reply')"

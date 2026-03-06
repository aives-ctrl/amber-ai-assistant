#!/bin/bash

# update-exec-approvals-mcp.sh — Add MCP wrapper scripts to exec-approvals.json
# Run on Amber's machine ONCE during MCP migration setup.
#
# Adds mcp-read.sh to the allowlist (auto-approved for reads).
# mcp-write.sh is intentionally NOT added (requires Dave's approval via Telegram).

set -euo pipefail

APPROVALS_FILE="/Users/amberives/.openclaw/exec-approvals.json"

if [ ! -f "$APPROVALS_FILE" ]; then
    echo "ERROR: exec-approvals.json not found at $APPROVALS_FILE"
    exit 1
fi

# Back up first
cp "$APPROVALS_FILE" "${APPROVALS_FILE}.pre-mcp-backup"
echo "Backed up to ${APPROVALS_FILE}.pre-mcp-backup"

python3 -c "
import json

with open('${APPROVALS_FILE}', 'r') as f:
    data = json.load(f)

main_list = data.get('agents', {}).get('main', {}).get('allowlist', [])

# MCP entries to add (read wrapper only — writes need approval)
entries_to_add = [
    {'id': 'mcp-read-basename', 'pattern': 'mcp-read.sh'},
    {'id': 'mcp-read-fullpath', 'pattern': '/Users/amberives/.openclaw/workspace/scripts/mcp-read.sh'},
]

existing_patterns = {e.get('pattern') for e in main_list}

for entry in entries_to_add:
    if entry['pattern'] not in existing_patterns:
        main_list.append(entry)
        print(f'Added: {entry[\"pattern\"]}')
    else:
        print(f'Already exists: {entry[\"pattern\"]}')

# SECURITY: Verify mcp-write.sh is NOT in the allowlist
for e in main_list:
    if 'mcp-write' in e.get('pattern', ''):
        print(f'WARNING: Removing mcp-write from allowlist (must require approval)')
        main_list.remove(e)

data['agents']['main']['allowlist'] = main_list

with open('${APPROVALS_FILE}', 'w') as f:
    json.dump(data, f, indent=2)

print('Done. mcp-read.sh is auto-approved. mcp-write.sh requires Telegram approval.')
"

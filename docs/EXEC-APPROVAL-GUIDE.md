# Exec-Approval Guide: Separating Read vs. Write Permissions in OpenClaw

## The Problem

OpenClaw's exec-approval system matches on **binary paths only**. When your AI assistant uses a single CLI tool (like `gog`) for both safe reads and dangerous writes, the approval system can't distinguish between them:

- `gog gmail messages search 'is:unread'` → safe read, should auto-approve
- `gog gmail send --to someone@example.com` → sends email, needs human approval

Both resolve to `/usr/local/bin/gog`, so either **both** trigger approval (safe but slow — your assistant needs you to approve every inbox check) or **both** auto-approve (fast but dangerous — your assistant can send emails without asking).

## The Solution: Wrapper Scripts

Create thin wrapper scripts that validate the subcommand before passing through to the real binary. Put these scripts on the exec-approval allowlist. Your assistant calls the wrappers (full path) for reads, and the raw binary for writes.

```
Read:  /path/to/gog-email-read.sh gmail messages search ...
       → wrapper is allowlisted → auto-approved → runs instantly

Write: gog gmail send --to someone@example.com
       → gog binary is NOT allowlisted → exec-approval fires → human approves
```

### Wrapper Script Structure

Each wrapper has an allowlist of safe subcommands and a blocklist of dangerous ones:

```bash
#!/bin/bash
# gog-email-read.sh — Allowlisted wrapper for READ-ONLY email operations

CMD="$*"

ALLOWED_PATTERNS=(
    "gmail messages search"
    "gmail messages get"
    "gmail messages list"
    "gmail thread get"
    "gmail thread list"
    "gmail labels list"
    "gmail labels get"
    # Include singular AND plural forms if your CLI accepts both
    "gmail message search"
    "gmail message get"
    "gmail message list"
)

BLOCKED_PATTERNS=(
    "gmail send"
    "gmail reply"
    "gmail draft"
    "gmail messages delete"
    "gmail messages trash"
)

# Check blocklist first (safety)
for pattern in "${BLOCKED_PATTERNS[@]}"; do
    if [[ "$CMD" == *"$pattern"* ]]; then
        echo "ERROR: This wrapper does NOT allow destructive operations."
        exit 1
    fi
done

# Check allowlist
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
    echo "ERROR: Command not in allowlist."
    exit 1
fi
```

### Key Design Decisions

1. **Full paths in documentation.** Tell your assistant to use `/full/path/to/gog-email-read.sh` in all skill docs. Don't rely on PATH — it's one more thing that can break.

2. **Blocklist before allowlist.** Check dangerous patterns first. Defense in depth.

3. **Singular AND plural forms.** If your CLI accepts both `gmail message get` and `gmail messages get`, add both to the wrapper. The assistant will use whichever form it feels like.

4. **One wrapper per permission level.** We use three:
   - `gog-email-read.sh` — read-only email operations
   - `gog-email-tag.sh` — email labeling (modify thread labels)
   - `gog-cal-read.sh` — read-only calendar operations

## What We Tried That Didn't Work

### Attempt 1: OpenClaw Plugin (gog-guard)

**Idea:** Write a `before_tool_call` hook plugin that intercepts `gog` commands and rewrites reads to use the wrapper scripts transparently. The assistant uses `gog` for everything; the plugin handles routing.

**Why it failed:** The plugin never loaded. We tried:
- CommonJS format (`module.exports`) → wrong; OpenClaw requires ESM (`export default`)
- Symlinks in `~/.openclaw/extensions/` → not followed by the plugin loader
- Direct file copy to `~/.openclaw/extensions/` → files present but plugin still invisible
- Removing TypeScript imports (`openclaw/plugin-sdk`) → module resolution may fail for user plugins outside the OpenClaw package
- Creating `~/.openclaw/config.json` with `plugins.entries.gog-guard.enabled: true` → no effect
- Adding `plugins.load.paths` pointing to the plugin directory → no effect
- `openclaw plugins install` and `openclaw plugins enable` → both hung indefinitely

**Conclusion:** OpenClaw's user plugin system (as of v2026.3.2) appears to have issues loading plugins from `~/.openclaw/extensions/`. The CLI commands for plugin management frequently hang. Built-in plugins (in the OpenClaw package at `/opt/homebrew/lib/node_modules/openclaw/extensions/`) load fine, but user-installed plugins don't.

**The plugin approach is theoretically cleaner** (transparent rewriting, assistant doesn't need to know about wrappers), but in practice it was unreliable. We kept the plugin code in `plugins/gog-guard/` for future reference in case OpenClaw's plugin system improves.

### Attempt 2: Basename Allowlist Entries

**Idea:** Add just the script name (e.g., `gog-email-read.sh`) to the exec-approval allowlist, relying on PATH resolution.

**Why it failed:** The scripts directory wasn't in PATH, so the shell couldn't find the basename. Even after adding to PATH via `~/.zshrc`, the OpenClaw gateway environment didn't always pick it up.

**Lesson:** Don't rely on PATH for security-critical scripts. Use full paths.

## What Worked

**Direct wrapper script calls with full paths.** No plugin, no PATH dependency. The assistant's skill docs contain the exact full-path commands:

```bash
# Email read (auto-approved)
/Users/amberives/.openclaw/workspace/scripts/gog-email-read.sh gmail messages search 'is:unread' --max 20

# Calendar read (auto-approved)
/Users/amberives/.openclaw/workspace/scripts/gog-cal-read.sh cal events daver@mindfireinc.com --from now --to +4h

# Email tag (auto-approved)
/Users/amberives/.openclaw/workspace/scripts/gog-email-tag.sh gmail thread modify <threadId> --add "Handled" --force

# Email send (requires human approval via Telegram)
gog gmail send --to "recipient@example.com" --subject "..." --body-html "..."
```

### Allowlist Configuration

In `~/.openclaw/exec-approvals.json`, the wrapper scripts are listed under `safeBinTrustedDirs` or individually. The key is that the resolved path of the wrapper script matches an allowlist entry.

## Setup Checklist

1. **Create wrapper scripts** in a known directory (e.g., `~/.openclaw/workspace/scripts/`)
2. **Make them executable:** `chmod +x gog-email-read.sh gog-cal-read.sh gog-email-tag.sh`
3. **Add to exec-approval allowlist** in `~/.openclaw/exec-approvals.json`
4. **Update skill docs** to use full wrapper paths for reads, bare `gog` for writes
5. **Restart gateway:** `pkill -f openclaw-gateway && sleep 2 && openclaw gateway restart`
6. **Test:** Run a read command (should auto-approve) and a write command (should trigger approval)

## Verification Tests

```bash
# Should auto-approve (no Telegram prompt):
/path/to/scripts/gog-email-read.sh gmail labels list
/path/to/scripts/gog-email-read.sh gmail messages search 'is:unread' --max 5
/path/to/scripts/gog-cal-read.sh cal events user@example.com --from now --to +4h

# Should trigger approval (Telegram prompt appears):
gog gmail send --to "test@example.com" --subject "Test" --body-html "<p>Test</p>"
```

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| Reads trigger approval | Using bare `gog` instead of wrapper path | Use full wrapper script path |
| "command not found" | Wrapper not at expected path | Verify path with `ls -la /path/to/script.sh` |
| "Permission denied" | Script not executable | `chmod +x /path/to/script.sh` |
| Wrapper rejects command | Subcommand not in allowlist | Add the pattern to the wrapper's `ALLOWED_PATTERNS` array |
| Sends don't trigger approval | `gog` binary somehow in allowlist | Remove it from `exec-approvals.json` |
| Gateway commands hang | Gateway in bad state | `pkill -f openclaw-gateway && sleep 2 && openclaw gateway restart` |

## Files

```
scripts/
  gog-email-read.sh    # Read-only email wrapper (allowlisted)
  gog-email-tag.sh     # Email tagging wrapper (allowlisted)
  gog-cal-read.sh      # Read-only calendar wrapper (allowlisted)

plugins/gog-guard/     # Plugin attempt (not currently active, kept for reference)
  index.ts             # before_tool_call hook to rewrite commands
  package.json         # OpenClaw plugin package config
  openclaw.plugin.json # Plugin manifest

skills/
  email-read/SKILL.md     # Uses gog-email-read.sh (full path)
  email-send/SKILL.md     # Uses gog for sends, gog-email-tag.sh for tagging
  calendar-read/SKILL.md  # Uses gog-cal-read.sh (full path)
  calendar-create/SKILL.md # Uses gog for creates (approval required)
```

---

*Last updated: 2026-03-05*
*Authors: Dave Rosendahl, Claude Code*

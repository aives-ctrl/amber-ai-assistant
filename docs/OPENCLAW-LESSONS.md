# OpenClaw Lessons Learned

Hard-won knowledge from building and operating an OpenClaw AI assistant. Each entry documents a real problem, what we tried, and what actually worked — so future-you (or anyone else) doesn't repeat the same debugging marathon.

---

## 1. Subcommand-Level Exec-Approval (Read vs. Write Permissions)

**Date:** 2026-03-05
**Severity:** Blocked all autonomous email/calendar operations
**Time to resolve:** ~8 hours across multiple sessions

### The Problem

OpenClaw's exec-approval system matches on **binary paths only**. When your assistant uses a single CLI tool (like `gog`) for both safe reads and dangerous writes, the approval system can't distinguish between them:

- `gog gmail messages search 'is:unread'` → safe read, should auto-approve
- `gog gmail send --to someone@example.com` → sends email, needs human approval

Both resolve to `/usr/local/bin/gog`. So either **both** need approval (safe but painfully slow) or **both** auto-approve (fast but dangerous).

### What We Tried That Failed

#### Attempt 1: OpenClaw Plugin (`before_tool_call` hook)

**Idea:** Write a plugin that intercepts `gog` commands and transparently rewrites reads to use allowlisted wrapper scripts. The assistant uses `gog` for everything; the plugin handles routing behind the scenes.

**Why it failed:** The plugin never loaded despite extensive troubleshooting:
- CommonJS format (`module.exports`) → wrong; OpenClaw requires ESM (`export default`)
- Symlinks in `~/.openclaw/extensions/` → not followed by the plugin loader
- Direct file copy to `~/.openclaw/extensions/` → files present but plugin still invisible
- Removing TypeScript imports (`openclaw/plugin-sdk`) → module resolution may fail for user plugins outside the OpenClaw package directory
- Creating `~/.openclaw/config.json` with `plugins.entries.<id>.enabled: true` → no effect
- Adding `plugins.load.paths` pointing to the plugin directory → no effect
- `openclaw plugins install` and `openclaw plugins enable` → both hung indefinitely

**Takeaway:** OpenClaw's user plugin system (v2026.3.2) appears to have issues loading plugins from `~/.openclaw/extensions/`. Built-in plugins load fine; user-installed ones don't. The CLI commands for plugin management frequently hang. The plugin approach is theoretically cleaner but wasn't viable.

#### Attempt 2: Basename Allowlist Entries

**Idea:** Add just the script name (e.g., `gog-email-read.sh`) to the allowlist, relying on PATH resolution.

**Why it failed:** The scripts directory wasn't in PATH. Even after adding to `~/.zshrc`, the OpenClaw gateway environment didn't always pick it up.

**Takeaway:** Don't rely on PATH for security-critical scripts. Use full absolute paths.

### What Actually Worked

**Direct wrapper script calls with full absolute paths.** No plugin, no PATH dependency.

Create thin bash wrapper scripts that validate subcommands against an allowlist/blocklist, then `exec gog $CMD` if approved. Put the wrappers on the exec-approval allowlist. Update the assistant's skill docs to call wrappers (full path) for reads and bare `gog` for writes.

```
Read:  /full/path/to/gog-email-read.sh gmail messages search ...
       → wrapper is allowlisted → auto-approved → runs instantly

Write: gog gmail send --to someone@example.com
       → gog binary NOT allowlisted → exec-approval fires → human approves
```

#### Wrapper Script Pattern

```bash
#!/bin/bash
CMD="$*"

ALLOWED_PATTERNS=("gmail messages search" "gmail messages get" "gmail labels list")
BLOCKED_PATTERNS=("gmail send" "gmail reply" "gmail delete" "gmail trash")

# Blocklist first (defense in depth)
for pattern in "${BLOCKED_PATTERNS[@]}"; do
    [[ "$CMD" == *"$pattern"* ]] && echo "BLOCKED: $pattern" && exit 1
done

# Allowlist check
for pattern in "${ALLOWED_PATTERNS[@]}"; do
    [[ "$CMD" == *"$pattern"* ]] && exec gog $CMD
done

echo "ERROR: Command not in allowlist." && exit 1
```

#### Key Design Decisions

1. **Full absolute paths in skill docs** — don't rely on PATH
2. **Blocklist before allowlist** — check dangerous patterns first
3. **Singular AND plural forms** — add both `gmail message get` and `gmail messages get` because the LLM uses whichever it wants
4. **One wrapper per permission level** — separate scripts for reads, tags, and calendar reads

### Setup Checklist

1. Create wrapper scripts in a known directory
2. `chmod +x` each script
3. Add scripts to `exec-approvals.json` allowlist (via `safeBinTrustedDirs` or individual entries)
4. Update skill docs to use full wrapper paths for reads, bare binary for writes
5. Restart gateway: `pkill -f openclaw-gateway && sleep 2 && openclaw gateway restart`
6. Test: read should auto-approve, write should trigger approval

### Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| Reads trigger approval | Using bare `gog` instead of wrapper | Use full wrapper script path |
| "command not found" | Wrong path or script missing | `ls -la /path/to/script.sh` |
| "Permission denied" | Script not executable | `chmod +x /path/to/script.sh` |
| Wrapper rejects command | Subcommand not in allowlist | Add pattern to wrapper's `ALLOWED_PATTERNS` |
| Sends don't trigger approval | `gog` binary in allowlist | Remove from `exec-approvals.json` |
| Gateway commands hang | Gateway bad state | `pkill -f openclaw-gateway && sleep 2 && openclaw gateway restart` |

### Files

```
scripts/gog-email-read.sh     # Read-only email wrapper
scripts/gog-email-tag.sh      # Email tagging wrapper
scripts/gog-cal-read.sh       # Read-only calendar wrapper
plugins/gog-guard/             # Plugin attempt (kept for reference, not active)
```

---

## 2. Gateway Instability and Hung CLI Commands

**Date:** 2026-03-05
**Severity:** Blocks all debugging and configuration
**Frequency:** Recurring (happened 5+ times in one session)

### The Problem

OpenClaw CLI commands (`openclaw plugins list`, `openclaw plugins enable`, `openclaw config get`) frequently hang indefinitely. The gateway gets into a bad state where it stops responding to CLI requests but continues running the assistant.

### What Worked

Hard kill + restart:

```bash
pkill -f openclaw-gateway && sleep 2 && openclaw gateway restart
```

The `sleep 2` is important — without it, the restart can fail because the old process hasn't fully released its port yet.

### Takeaway

If any `openclaw` CLI command hangs for more than 10 seconds, don't wait — kill and restart. The gateway recovers cleanly from hard restarts. This is a known rough edge as of v2026.3.2.

---

## 3. `openclaw plugins link` Doesn't Exist

**Date:** 2026-03-05
**Severity:** Misleading documentation / wasted time

### The Problem

We assumed `openclaw plugins link <path>` was a command (similar to `npm link`). It's not a standalone command — it's a flag:

```bash
# This doesn't exist:
openclaw plugins link /path/to/plugin

# This is the actual command:
openclaw plugins install -l /path/to/plugin
```

The `-l` flag creates a symlink instead of copying. However, even this approach didn't work for us (see Lesson #1 — symlinks weren't followed by the loader).

### Takeaway

When installing plugins manually, use `openclaw plugins install <path>` (copies files) rather than `-l` (symlinks). Or skip the CLI entirely and place files directly in `~/.openclaw/extensions/<plugin-id>/`.

---

## 4. OpenClaw Plugin Format Requirements

**Date:** 2026-03-05
**Severity:** Silent failure (plugin just doesn't load, no error)

### The Problem

We initially wrote the plugin using CommonJS patterns. OpenClaw requires a specific ESM format, and there's no error message when you get it wrong — the plugin just silently doesn't load.

### Correct Format

**`package.json`** — must have `"type": "module"` and `"openclaw.extensions"`:
```json
{
  "name": "my-plugin",
  "version": "0.1.0",
  "type": "module",
  "openclaw": {
    "extensions": ["./index.ts"]
  }
}
```

**`openclaw.plugin.json`** — plugin manifest:
```json
{
  "id": "my-plugin",
  "name": "My Plugin",
  "description": "What it does",
  "version": "0.1.0"
}
```

**`index.ts`** — ESM with `export default`, `register(api)`, `api.registerHook()`:
```typescript
import type { OpenClawPluginApi } from "openclaw/plugin-sdk";
import { emptyPluginConfigSchema } from "openclaw/plugin-sdk";

const plugin = {
  id: "my-plugin",
  name: "My Plugin",
  description: "...",
  configSchema: emptyPluginConfigSchema(),

  register(api: OpenClawPluginApi) {
    api.registerHook("before_tool_call", (event) => {
      // your hook logic
      return { params: event.params }; // to modify params
      // or return { block: true, blockReason: "..." }; // to block
    });
    api.logger.info("[my-plugin] Loaded");
  },
};

export default plugin;
```

### Common Mistakes

| Wrong | Right |
|-------|-------|
| `module.exports = function(api) {}` | `export default { register(api) {} }` |
| `api.on("before_tool_call", ...)` | `api.registerHook("before_tool_call", ...)` |
| Missing `"type": "module"` in package.json | Include it |
| `.js` extension | `.ts` extension |

### Takeaway

If your plugin doesn't appear in `openclaw plugins list`, the format is probably wrong. OpenClaw gives zero feedback about plugin load failures. Compare your plugin structure against a working built-in plugin at `/opt/homebrew/lib/node_modules/openclaw/extensions/`.

---

*Add new lessons below as you encounter them. Include the date, what went wrong, what you tried, and what fixed it.*

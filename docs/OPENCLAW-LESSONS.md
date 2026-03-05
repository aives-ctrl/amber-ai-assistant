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

## 5. Session Context Doesn't Reload After File Updates

**Date:** 2026-03-05
**Severity:** High — causes assistant to ignore fixes you just deployed
**Time to resolve:** ~1 hour of confusion

### The Problem

After Amber ran `./update-self.sh` (which updates config/skill files on disk), she tested the new wrapper script commands successfully — then immediately went back to using bare `gog` for all subsequent email reads. Every search triggered exec-approval, exactly the problem the update was supposed to fix.

### Root Cause

**The running LLM session doesn't re-read skill docs from disk.** When a session starts, OpenClaw loads config files and skill docs into the LLM context. Updating files on disk mid-session has zero effect — the LLM is still operating from whatever was loaded at session start.

So: Amber pulled updated docs telling her to use wrapper scripts. She tested the wrapper (by copy-pasting the exact command Dave gave her). Then she went back to processing emails using the patterns already in her context — which were the OLD patterns from before the update.

### The Fix

**After `./update-self.sh` or `git pull`, always run `/new` to start a fresh session.** The new session loads the updated docs from disk.

The pattern:
1. Push local changes (git sync)
2. Pull updates (`./update-self.sh`)
3. Start new session: `/new`
4. New session loads fresh docs

We added this as:
- A prominent warning in `update-self.sh` output
- A dedicated section in `AGENTS.md` ("After Pulling Updates: RESTART Your Session")

### Takeaway

Treat file updates to an OpenClaw assistant like deploying code to a running server — the changes aren't live until you restart. The LLM is not a filesystem watcher; it's a snapshot of context from session start.

---

## 6. Git Sync: AI Assistants That Edit Shared Repos Must Push Before Pulling

**Date:** 2026-03-05
**Severity:** Critical — silent data loss of accumulated lessons and daily notes
**Time to resolve:** ~30 minutes

### The Problem

Amber edits files at runtime (daily notes, email style lessons, follow-up tracker) that live in a git repo shared with Dave's machine. When Dave pushed config updates and Amber ran `git pull`, her uncommitted local changes were silently overwritten. Lessons she'd logged, daily notes she'd written — gone.

### Root Cause

`update-self.sh` ran `git pull origin main` without first committing and pushing Amber's local changes. Standard git behavior: pull overwrites dirty files.

### The Fix

Added Step 0 to `update-self.sh` — before pulling, auto-commit and push any changes to `memory/` and `config/follow-up-tracker.md`:

```bash
if [ -n "$(git status --porcelain)" ]; then
    git add memory/ config/follow-up-tracker.md
    if ! git diff --cached --quiet; then
        git commit -m "Amber: auto-sync local changes"
        git push origin main
    fi
fi
```

Also documented the manual sync command in AGENTS.md and skill docs for when Amber should push proactively (after logging lessons, writing daily notes, etc.).

### Takeaway

If your AI assistant writes to files in a shared repo, the update/pull script MUST commit+push first. This is easy to miss because the assistant doesn't complain — it just silently loses its accumulated knowledge.

---

## 7. LLM Lesson-Logging Requires Broad Triggers

**Date:** 2026-03-05
**Severity:** Medium — assistant doesn't learn from feedback
**Time to resolve:** ~20 minutes to diagnose, quick doc fix

### The Problem

Amber processed 8 emails with Dave giving feedback throughout. Zero new entries were logged to `email-style-lessons.md`. The lesson file wasn't even in her git push.

### Root Cause

The lesson-logging trigger in the docs was too narrow. It said: **"When Dave adjusts a draft..."** This only fired when Dave explicitly requested wording changes to a specific email draft. It missed:

- Process corrections ("you already replied to this one")
- Behavioral feedback ("use the wrapper script, not bare gog")
- General style guidance ("be more casual")
- Any feedback not tied to a specific draft revision

Dave gave feedback in all these categories, but none of them matched the "adjusts a draft" trigger, so Amber never logged them.

### The Fix

Broadened the trigger in both AGENTS.md and email-send SKILL.md:

**Old:** "When Dave adjusts a draft, log the lesson."
**New:** "Any time Dave gives you corrective feedback — drafts, process, behavior, style, preferences — log it as a lesson BEFORE moving on."

Added explicit examples of each feedback type so the LLM can pattern-match more broadly.

### Takeaway

When instructing an LLM to log/learn from feedback, make the trigger as broad as possible with concrete examples. LLMs interpret narrow triggers literally. "When Dave adjusts a draft" → only draft adjustments. "When Dave gives ANY corrective feedback" + 5 examples → much broader coverage. The more specific your examples, the more patterns the LLM will catch.

---

## 8. Doc-Level Enforcement Fails for LLM Tool Usage — Use Structural Interception

**Date:** 2026-03-05
**Severity:** Critical — assistant ignores documented commands and invents its own
**Time to resolve:** ~10 hours across multiple sessions and 6 failed approaches

### The Problem

Amber's skill docs said "ALWAYS use the full wrapper script path `/Users/amberives/.openclaw/workspace/scripts/gog-email-read.sh`" and "NEVER use bare `gog` for reads." Despite this being documented in 3+ places, restated in bold, and reinforced across 4+ doc updates and multiple session restarts, she continued generating bare `gog` commands:

- `gog gmail messages search 'is:unread'` (should use wrapper)
- `gog gmail threads get <id>` (should use wrapper)
- `gog gmail inbox` (a subcommand that doesn't even exist in gog or the docs)

Each bare `gog` call resolved to `/usr/local/bin/gog`, which was not in the exec-approval allowlist, triggering approval prompts for safe read operations.

### What We Tried That Failed (6 attempts)

#### Attempt 1: Doc-level instructions (4+ iterations)

Updated skill docs to say "NEVER use bare gog," added warnings, bolded them, added troubleshooting sections. After each update, ran `/new` to reload context.

**Result:** She'd use the wrapper for a few commands, then revert to bare `gog`. The LLM's training-data patterns for CLI tool usage (`gog <subcommand>`) are stronger than in-context instructions telling her to use a different command.

#### Attempt 2: gog-guard plugin (before_tool_call hook)

Built a plugin to intercept `gog` at the OpenClaw tool layer and rewrite read commands to use wrapper scripts before exec-approval checked them.

**Result:** The plugin never loaded reliably. OpenClaw's user plugin system (v2026.3.2) has issues with user-installed plugins in `~/.openclaw/extensions/`. See Lesson #1 for details.

#### Attempt 3: Multiple session restarts

Thought maybe old context was persisting. Ran `/new` after every doc update.

**Result:** Fresh sessions loaded the updated docs correctly, but the LLM still generated bare `gog` from training patterns. The docs are read, but training-data patterns for CLI usage override them during generation.

#### Attempt 4: `pathPrepend` config

Set `tools.exec.pathPrepend` to include the scripts directory, hoping OpenClaw would resolve `gog` to the wrapper.

**Result:** `pathPrepend` only affects child shell environments spawned by the exec tool. It does NOT affect the gateway's own binary resolution for exec-approval decisions. The gateway still resolved `gog` to `/usr/local/bin/gog`.

#### Attempt 5: Symlink in `/opt/homebrew/bin/`

Created a symlink at `/opt/homebrew/bin/gog` → `scripts/gog`, since `/opt/homebrew/bin` was listed in `safeBinTrustedDirs`.

**Result:** `/opt/homebrew/bin` does NOT exist on Intel Macs. Amber's MacBook Air is Intel — Homebrew installs to `/usr/local` on Intel, `/opt/homebrew` on Apple Silicon. The symlink target directory simply didn't exist. Wasted hours debugging before discovering this with `brew --prefix` → `/usr/local`.

#### Attempt 6: Soft gateway restarts

After adding the scripts directory to `~/.zshrc` PATH, ran `openclaw gateway restart`.

**Result:** Soft restarts may not spawn a new process that inherits the updated PATH. The existing gateway process kept its old PATH. Binary resolution still pointed to `/usr/local/bin/gog`.

### What Actually Worked

**PATH wrapper script + hard gateway kill.** Two pieces, both required:

1. **The wrapper:** A bash script named `gog` in the scripts directory (which is in `safeBinTrustedDirs`). It intercepts bare `gog` calls. For safe read patterns, it calls the real binary via `exec` (subprocess inherits auto-approval). For dangerous write patterns, it BLOCKS with an error message.

2. **Hard kill + restart from correct shell:** `pkill -f openclaw-gateway && sleep 2 && openclaw gateway restart` from a shell where `which gog` returns the wrapper path. The gateway inherits PATH at startup. A soft restart doesn't create a new process.

```
Read:  gog gmail messages search 'is:unread'
       → gateway resolves to scripts/gog (wrapper, in safeBinTrustedDirs)
       → auto-approved (trusted directory)
       → wrapper matches safe pattern → exec /usr/local/bin/gog "$@"
       → command runs instantly

Write: gog gmail send --to someone@example.com
       → gateway resolves to scripts/gog (wrapper, in safeBinTrustedDirs)
       → auto-approved
       → wrapper matches dangerous pattern → BLOCKS with error
       → LLM retries with /usr/local/bin/gog (from skill docs)
       → NOT in trusted dir → exec-approval fires → Dave approves
```

The key insight: **don't fight the LLM's training-data patterns — intercept them at the system level.** Let it generate whatever `gog` commands it wants, and route them appropriately before they hit the approval system.

### Design Decisions

1. **Wrapper BLOCKS dangerous commands** (doesn't pass through) — because the wrapper is in a trusted directory and auto-approves, passing sends through via `exec` would bypass approval entirely. Blocking forces the LLM to use the full path `/usr/local/bin/gog` for writes.
2. **Unknown commands also BLOCK** — safe default; new/invented subcommands get blocked rather than silently auto-approved
3. **No doc changes needed for the LLM** — the wrapper is invisible to Amber. She uses bare `gog` for reads (works via wrapper). Send commands in skill docs use `/usr/local/bin/gog` (full path, bypasses wrapper, triggers approval).
4. **Lives in the git repo** — updated via `git pull` like everything else

### Setup

1. Script at `scripts/gog` (already in repo)
2. Add scripts dir to PATH before `/usr/local/bin`: `export PATH="/path/to/scripts:$PATH"` in `~/.zshrc`
3. `chmod +x scripts/gog`
4. **Hard kill** gateway: `pkill -f openclaw-gateway && sleep 2 && openclaw gateway restart`
5. Verify: `which gog` → should show the scripts directory, not `/usr/local/bin`

### ⚠️ Fragility: Reboots and Gateway Restarts

The gateway inherits PATH from the shell that starts it. If the gateway restarts from a non-interactive context (launchd, crash recovery), `~/.zshrc` may not be read, so the scripts directory won't be in PATH. Reads will start triggering approval again.

**Recovery (run from any terminal):**
```bash
export PATH="/Users/amberives/.openclaw/workspace/scripts:$PATH" && pkill -f openclaw-gateway && sleep 2 && openclaw gateway restart
```

**Symptom:** If `gog gmail labels list` starts prompting for approval, run the recovery command above.

### Takeaway

When an LLM assistant consistently ignores doc-level instructions for tool usage, the problem isn't the docs — it's that training-data patterns are stronger than in-context instructions during generation. The fix is to intercept at the system level (PATH, shell wrapper, proxy) rather than continuing to update docs. This is the same principle as using guardrails/filters instead of relying on prompt engineering alone.

**Additional takeaways:**
- Always verify Homebrew paths — Intel Macs use `/usr/local`, Apple Silicon uses `/opt/homebrew`. Run `brew --prefix` to check.
- `pathPrepend` affects child shells, NOT gateway binary resolution.
- Soft `openclaw gateway restart` may not spawn a new process. Always use `pkill -f openclaw-gateway` for config/PATH changes.
- OpenClaw's exec-approval system is binary-path only — no subcommand matching. This is confirmed in the [official docs](https://docs.openclaw.ai/tools/exec-approvals). GitHub issue #2023 requested tool-level HITL for messaging; it was closed without implementation.

---

*Add new lessons below as you encounter them. Include the date, what went wrong, what you tried, and what fixed it.*

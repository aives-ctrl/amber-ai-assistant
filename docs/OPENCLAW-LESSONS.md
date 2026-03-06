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

## 9. OpenClaw Resolves Symlinks — Use Hard Copies in Trusted Dirs

**Date:** 2026-03-05
**Severity:** Critical — completely defeats auto-approval mechanism
**Time to resolve:** ~2 hours

### The Problem

After building the `gog` PATH wrapper (Lesson #8), we needed `gog-real` in the trusted scripts dir to avoid triggering exec-approval on the `exec` call. We created a symlink:

```bash
ln -sf /usr/local/bin/gog /Users/amberives/.openclaw/workspace/scripts/gog-real
```

All wrapper scripts were updated to `exec gog-real` instead of `exec /usr/local/bin/gog`. But reads and tags **still** triggered exec-approval.

### Root Cause

**OpenClaw resolves symlinks to their real path before checking `safeBinTrustedDirs`.** The symlink `scripts/gog-real → /usr/local/bin/gog` resolved to `/usr/local/bin/gog`, which is NOT in the trusted dir. So OpenClaw still saw an untrusted binary execution.

This was invisible from terminal testing — running `gog gmail labels list` in a terminal worked fine because the terminal doesn't have OpenClaw's exec monitoring. The approval check only happens when the LLM agent executes commands through OpenClaw.

### What We Tried That Failed

1. **Symlink (`ln -sf`)** — OpenClaw resolves it to real path → triggers approval
2. **`cp` on top of existing symlink** — `cp /usr/local/bin/gog .../gog-real` returned "are identical (not copied)" because `cp` followed the symlink and saw source and destination as the same file

### What Actually Worked

**Remove the symlink first, then hard copy:**

```bash
rm /Users/amberives/.openclaw/workspace/scripts/gog-real
cp /usr/local/bin/gog /Users/amberives/.openclaw/workspace/scripts/gog-real
```

Then hard-restart the gateway:
```bash
pkill -f openclaw-gateway && sleep 2 && openclaw gateway restart
```

A hard copy creates a real file in the trusted dir. OpenClaw checks the file's actual path (`scripts/gog-real`) — it IS in `safeBinTrustedDirs` — auto-approved.

### The Working Architecture

```
gog (wrapper, trusted dir)
  → matches safe pattern → exec gog-real (HARD COPY in trusted dir) → auto-approved ✅
  → matches dangerous pattern → BLOCKS → LLM uses /usr/local/bin/gog → approval fires ✅
```

### Maintenance

After `gog` binary updates (e.g., `brew upgrade`), re-copy:
```bash
rm /Users/amberives/.openclaw/workspace/scripts/gog-real
cp /usr/local/bin/gog /Users/amberives/.openclaw/workspace/scripts/gog-real
pkill -f openclaw-gateway && sleep 2 && openclaw gateway restart
```

`gog-real` is in `.gitignore` because it's a machine-specific binary that shouldn't be in the repo.

### Takeaway

OpenClaw's `safeBinTrustedDirs` check resolves symlinks before matching. A symlink in a trusted dir pointing to a binary outside the trusted dir will NOT auto-approve. Use a hard copy (`cp`) instead. This is a subtle security behavior — the system prevents symlink-based trust escalation, which is arguably correct from a security perspective, but it's undocumented and cost us hours of debugging.

---

## 10. Glob `gog-*` Does NOT Match `gog` — Add Explicit Allowlist Entry for Wrapper

**Date:** 2026-03-05
**Severity:** Critical — tags and thread modify operations triggered approval despite wrapper being in trusted dir
**Time to resolve:** ~3 hours

### The Problem

After getting reads working through the gog PATH wrapper (Lessons #8 and #9), thread tagging (`gog gmail thread modify`) still triggered exec-approval. Reads worked perfectly — only tag/modify operations prompted for approval.

### Root Cause

The exec-approval allowlist had a glob entry:
```
/Users/amberives/.openclaw/workspace/scripts/gog-*
```

This matches `gog-email-read.sh`, `gog-email-tag.sh`, `gog-cal-read.sh`, and `gog-real` — all of which have a **dash** after "gog". But `gog-*` does **NOT** match `gog` (the wrapper script itself, which has no dash).

**Why reads worked anyway:** Amber was calling `gog-email-read.sh` directly (matched by both the glob and individual full-path entries). Tags failed because Amber called bare `gog` → resolved to `scripts/gog` → no allowlist match → approval triggered.

### Debugging

Dumped the full allowlist to confirm:
```bash
python3 -c "
import json
with open('/Users/amberives/.openclaw/exec-approvals.json','r') as f: data=json.load(f)
for e in data['agents']['main']['allowlist']:
    if 'gog' in e.get('pattern','').lower():
        print(e)
"
```

Output showed `gog-*` glob but no entry for `scripts/gog` itself.

### What Fixed It

Added an explicit allowlist entry for the wrapper:
```bash
python3 -c "
import json
with open('/Users/amberives/.openclaw/exec-approvals.json','r') as f: data=json.load(f)
ml=data['agents']['main']['allowlist']
ml.append({'id':'gog-wrapper','pattern':'/Users/amberives/.openclaw/workspace/scripts/gog'})
data['agents']['main']['allowlist']=ml
with open('/Users/amberives/.openclaw/exec-approvals.json','w') as f: json.dump(data,f,indent=2)
print('Added gog wrapper entry')
" && pkill -f openclaw-gateway && sleep 2 && openclaw gateway restart
```

After applying + gateway restart, `gog gmail thread modify <threadId> --add "Handled" --force` auto-approved immediately.

### The Complete Working Allowlist (gog-related)

```
gog-email-read      → /Users/amberives/.openclaw/workspace/scripts/gog-email-read.sh
gog-cal-read        → /Users/amberives/.openclaw/workspace/scripts/gog-cal-read.sh
gog-email-tag       → /Users/amberives/.openclaw/workspace/scripts/gog-email-tag.sh (if present)
gog-scripts-glob    → /Users/amberives/.openclaw/workspace/scripts/gog-*
gog-wrapper         → /Users/amberives/.openclaw/workspace/scripts/gog   ← THIS WAS MISSING
```

### Takeaway

Shell glob `gog-*` requires at least one character after the dash. It does NOT match `gog` with no suffix. When your wrapper script has a different name pattern than the scripts it wraps, you need a separate allowlist entry for it. Always dump the full allowlist and test each binary path against each pattern when debugging approval issues.

**Also: don't trust the LLM's diagnostic output.** During debugging, Amber confidently stated `exec-approvals.json` doesn't exist (it's 27KB). We had to run the diagnostic command directly on her machine to get accurate results. Trust but verify.

---

## 11. Use Smarter Models as Verifiers, Not Replacements — Opus Pre-Flight for Sends

**Date:** 2026-03-05
**Severity:** Recurring — same mistakes (threading, CC drops) happened 3+ times in one day
**Time to resolve:** Ongoing; this is the architectural solution

### The Problem

Amber (running Sonnet 4) keeps making the same email mistakes despite:
- Doc-level instructions (SKILL.md, bolded, repeated, with examples)
- Structural wrappers (gog wrapper with hard blocks)
- Logged lessons (email-style-lessons.md with dates and names)
- Multiple session restarts

The mistakes aren't intelligence failures — she *knows* the rules when prompted. They're **attention and consistency** failures, which is where model tier matters. Sonnet is fast and cost-effective but doesn't reliably follow multi-step checklists.

### What Doesn't Work (Reliably)

1. **Adding more docs** — Lesson #8 established this. LLM training patterns override in-context instructions.
2. **Making docs more emphatic** — Bold, caps, shame ("you did this with Bob on 3/5") helps somewhat but isn't reliable.
3. **Structural wrapper blocks** — Catches errors WHEN Amber routes through the wrapper, but she sometimes calls `/usr/local/bin/gog` directly, bypassing it.

### What We Built

**Opus 4.6 verifier step in a Lobster workflow** (`workflows/email-send.lobster.yaml`):

1. Amber drafts the email and gathers parameters (original headers, messageId, body)
2. She invokes `lobster run /path/to/email-send.lobster.yaml` with those parameters
3. **Opus 4.6** reviews the parameters: Is `--reply-to-message-id` used for replies? Is `--reply-all` present? Is `--body-html` used? Does the signature match?
4. If Opus says FAIL → workflow stops, Amber sees specific errors
5. If Opus says PASS → gog send executes (triggering exec-approval for Dave)
6. After send succeeds → auto-tag Handled

**Key architectural insight:** Use the fast model (Sonnet) for creative work (drafting, reasoning, triage). Use the smart model (Opus) for **validation** — a cheap, structured yes/no check. The Opus call costs fractions of a cent (tiny prompt, JSON output, temp=0) but catches every mistake we've seen.

### Configuration

- `openclaw-fixed.json`: Added `llm-task` plugin config with `allowedModels` including Opus
- `workflows/email-send.lobster.yaml`: Lobster workflow with `llm-task` verifier step
- `skills/email-send/SKILL.md`: Updated to reference workflow as preferred send method
- `config/TOOLS.md`: Lists the new workflow

### The Pattern (Generalizable)

This is the **verifier sub-agent pattern**:
- Fast model does the work (drafts, categorizes, reasons)
- Smart model checks the work (validates, catches errors)
- Deterministic orchestration (Lobster) enforces the order
- Structural wrappers (gog) provide defense-in-depth

Apply this pattern to ANY operation where:
1. The fast model keeps making the same mistake
2. The mistake is detectable by reviewing the command/output
3. The cost of an Opus call is negligible compared to the cost of the mistake

### Takeaway

Don't replace your fast model with a smarter one for everything — that's expensive. Instead, use the smarter model as a **checkpoint** at critical moments. Think of it as a senior reviewer who spends 2 seconds checking a junior's work before it goes out the door.

---

## 12. CLI Allowlist Commands Don't Work for Agent-Specific Allowlists

**Date:** 2026-03-05
**Severity:** Critical — causes double-approval for workflow orchestrators
**Time to resolve:** ~2 hours across sessions

### The Problem

After building the Lobster email-send workflow, `lobster run email-send` triggered exec-approval for the `lobster` binary itself — AND the internal `/usr/local/bin/gog gmail send` triggered a second approval. Dave had to approve twice, and the second often expired before he could act on it.

We ran `openclaw config set exec.allow '["lobster"]' --merge` on Amber's machine. Amber reported "Already allowlisted." But `lobster run` still triggered exec-approval.

### Root Cause

OpenClaw has **three** places where allowlist entries can live:

1. **`agents.main.allowlist`** in `exec-approvals.json` — the ONLY one consulted for the main agent
2. **`agents.*.allowlist`** in `exec-approvals.json` — wildcard fallback, never consulted when `agents.main` exists
3. **`exec.allow`** in `openclaw.json` — unknown/different mechanism

The CLI commands (`openclaw config set exec.allow`, `openclaw approvals allowlist add`) add to options 2 or 3. They report "Already allowlisted" because lobster IS in one of those locations — it's just not in the one that matters (`agents.main.allowlist`).

This is the SAME lesson as the gog wrapper scripts (Lesson #10 / AMBER-SETUP-INSTRUCTIONS Step 2). We knew CLI commands don't work for `agents.main.allowlist`. But we forgot to apply this knowledge when allowlisting a new binary (lobster).

### The Fix

Edit `exec-approvals.json` directly to add lobster to `agents.main.allowlist`:

```bash
python3 -c "
import json, subprocess
with open('/Users/amberives/.openclaw/exec-approvals.json', 'r') as f:
    data = json.load(f)
main_list = data['agents']['main']['allowlist']
result = subprocess.run(['which', 'lobster'], capture_output=True, text=True)
lobster_path = result.stdout.strip()
entries = [{'id': 'lobster-basename', 'pattern': 'lobster'}]
if lobster_path:
    entries.append({'id': 'lobster-full-path', 'pattern': lobster_path})
existing = {e.get('pattern') for e in main_list}
for e in entries:
    if e['pattern'] not in existing:
        main_list.append(e)
        print(f'Added: {e[\"pattern\"]}')
data['agents']['main']['allowlist'] = main_list
with open('/Users/amberives/.openclaw/exec-approvals.json', 'w') as f:
    json.dump(data, f, indent=2)
print('Done.')
" && pkill -f openclaw-gateway && sleep 2 && openclaw gateway restart
```

### Takeaway

**Every time you need to allowlist a new binary for the main agent, edit `exec-approvals.json` directly.** The CLI commands are unreliable for this. Make this a hard rule:

- New gog wrapper script → edit `exec-approvals.json` → add to `agents.main.allowlist`
- New orchestrator (lobster, etc.) → edit `exec-approvals.json` → add to `agents.main.allowlist`
- Never trust `openclaw config set exec.allow` or `openclaw approvals allowlist add` for the main agent

The CLI may show "Already allowlisted" because it found the entry somewhere — but "somewhere" isn't `agents.main.allowlist`, so the main agent never sees it.

---

## 13. Lobster Child Processes Bypass Exec-Approval — Design Workflows Accordingly

**Date:** 2026-03-05
**Severity:** Critical — workflow silently fails, no email sent
**Time to resolve:** ~4 hours across sessions + documentation research

### The Problem

The email-send Lobster workflow ran without errors, but no email was sent. The workflow completed (session disappeared), no approval requests were pending, and the sent folder was empty. It failed silently.

### Root Causes (Three of Them)

#### 1. `openclaw.invoke` needs `OPENCLAW_URL` env var

The verify step used `openclaw.invoke --tool llm-task` to call Opus. `openclaw.invoke` is a real CLI command (shim installed by npm) that communicates with the OpenClaw Gateway over WebSocket RPC. It requires the `OPENCLAW_URL` environment variable to connect.

When lobster spawns child processes (via `/bin/sh`), these env vars are NOT automatically set. The `openclaw.invoke` call silently failed because it couldn't reach the Gateway. Since the verify step produced no valid JSON output, `$verify.json.approved` was never `true`, so the send step was skipped.

**Fix:** Add `env: { OPENCLAW_URL: "http://localhost:18789" }` to any workflow step that uses `openclaw.invoke`.

#### 2. Lobster child processes bypass exec-approval

This is the architectural misunderstanding. Lobster runs commands via `/bin/sh` as direct subprocesses. These child processes do NOT go through OpenClaw's exec-approval pipeline. OpenClaw's exec-approval only applies to commands the AGENT runs via the exec tool — not to grandchild processes spawned by an already-approved command.

So `/usr/local/bin/gog gmail send` inside a lobster step would either:
- Execute without any approval (security hole), or
- Fail because it lacks the OpenClaw exec context

The old workflow relied on exec-approval as the send gate — but that gate doesn't exist inside lobster.

**Fix:** Use `gog-real` (hard copy in the trusted scripts dir) for the send step, and rely on:
- Dave's draft approval (SKILL.md step 6) as the content gate
- Opus verification (workflow step 1) as the technical gate

Lobster's own `approval: required` mechanism is also available for workflows that need explicit pause-and-approve gates.

#### 3. Raw `${arg}` substitution breaks on HTML content

The old workflow used `${body_html}` directly in YAML command strings. HTML content contains quotes, angle brackets, and special characters that break shell command construction. YAML Issue #29491 documents this limitation.

**Fix:** Use `$LOBSTER_ARG_<NAME>` env vars in step `env:` blocks, then reference with proper shell quoting (`"$VAR"`). For complex JSON construction, use `jq -n --arg` for safe escaping. For the verify step, we extracted the logic into a standalone script (`scripts/verify-email-send.sh`) that reads from LOBSTER_ARG env vars.

### What We Tried That Failed

1. **Adding lobster to `agents.main.allowlist`** — Both basename and full path entries were added. They were confirmed present (194 entries, both found, path matched). But lobster still triggered exec-approval. This was a red herring — the allowlist approach works for the lobster binary itself, but the real problem was inside the workflow.

2. **Adding `/usr/local/bin` to `safeBinTrustedDirs`** — Rejected because raw `gog` lives there. Adding it would auto-approve ALL gog commands, bypassing the send gate entirely.

3. **Copying lobster to the scripts directory** — Unlike gog (a standalone binary), lobster is an npm package with module dependencies. A simple `cp` doesn't work.

### The Working Architecture

```
Dave says "send it" in Telegram (content approval)
  → Amber runs: lobster run /Users/amberives/.openclaw/workspace/workflows/email-send.lobster.yaml --arg ...
    → lobster triggers exec-approval for itself (Dave approves once)
    → Step 1: verify-email-send.sh
      → sets OPENCLAW_URL env var
      → builds JSON safely via jq
      → calls openclaw.invoke --tool llm-task (Opus 4.6)
      → returns {approved: true/false, errors: [...]}
    → Step 2: report-failure (conditional, if verify failed)
    → Step 3: gog-real gmail send (conditional, if verify passed)
      → uses $LOBSTER_ARG_* env vars for safe quoting
      → gog-real is in trusted scripts dir → no approval
      → email sends directly
    → Step 4: gog-email-tag.sh (conditional, if send succeeded)
      → tags thread as Handled
```

The approval flow is now: **Draft review (human judgment) → Opus verify (automated check) → Direct send (no second approval)**. The exec-approval for the lobster binary itself still fires, but that's just confirming the workflow run.

### Key Files

```
scripts/verify-email-send.sh        # Opus verify via openclaw.invoke (reads LOBSTER_ARG_* env vars)
workflows/email-send.lobster.yaml   # Rewritten: env vars, gog-real, OPENCLAW_URL
skills/email-send/SKILL.md          # Updated: no exec-approval for sends, workflow handles everything
```

### Takeaways

1. **Lobster child processes bypass exec-approval.** Design workflows knowing this. Use lobster's `approval: required` gates for side-effect control, not exec-approval.
2. **`openclaw.invoke` needs `OPENCLAW_URL`** (and optionally `OPENCLAW_TOKEN`). Set these in step `env:` blocks.
3. **Never use raw `${arg}` substitution for user content in YAML commands.** Use `$LOBSTER_ARG_<NAME>` env vars with proper shell quoting instead.
4. **Silent failures are the norm in lobster.** If a step's command fails, the step output is empty/error, and conditional steps that check the output just skip. Add explicit error handling or use `set -euo pipefail` in scripts.
5. **Read the actual docs before building.** We built the original workflow from first principles and got the exec-approval architecture wrong. The lobster README and community examples clearly show the `approval: required` pattern as the correct approach.

---

## 14. Lobster Does Not Auto-Discover Custom Workflows — Use Full File Path

**Date:** 2026-03-05
**Severity:** Critical — workflow cannot be found, command fails immediately
**Time to resolve:** ~1 hour

### The Problem

`lobster run email-send` failed with "Error: Unknown command: email-send". The workflow file existed at `/Users/amberives/.openclaw/workspace/workflows/email-send.lobster.yaml`, but lobster couldn't find it. `lobster workflows.list` only showed built-in workflows (`github.pr.monitor`, `github.pr.monitor.notify`).

### Root Cause

Lobster does NOT automatically scan the OpenClaw workspace `workflows/` directory (or any directory) for custom `.lobster.yaml` files. The name-based `lobster run <name>` syntax only works for:
- Built-in workflows bundled with the lobster npm package
- Workflows registered in `~/.lobster/workflows/` (standard lobster directory)

Custom workflows in the OpenClaw workspace directory are invisible to lobster's name resolver.

### The Fix

Use the **full file path** instead of the workflow name:

```bash
# WRONG — lobster can't find this
lobster run email-send --arg ...

# CORRECT — full path, always works
lobster run /Users/amberives/.openclaw/workspace/workflows/email-send.lobster.yaml --arg ...
```

Updated all references in:
- `skills/email-send/SKILL.md` (3 locations)
- `workflows/email-send.lobster.yaml` (usage comment)
- `docs/AMBER-SETUP-INSTRUCTIONS.md` (test command + table)
- `config/HEARTBEAT.md` (daily learnings workflow)

### Takeaway

1. **Always use full file path for custom lobster workflows.** `lobster run <name>` is only for built-in workflows.
2. **Test the exact command your agent will run.** If we had tested `lobster run email-send` ourselves before giving it to Amber, we'd have caught this immediately.
3. **`lobster workflows.list` only shows registered/built-in workflows.** Don't use it to verify custom workflow availability — use `ls` on the workflow directory instead.

---

*Add new lessons below as you encounter them. Include the date, what went wrong, what you tried, and what fixed it.*

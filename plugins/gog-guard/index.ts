/**
 * gog-guard — OpenClaw plugin for subcommand-level exec-approval control
 *
 * PROBLEM: OpenClaw's exec-approval allowlist matches on binary paths only.
 * It can't distinguish between `gog gmail messages search` (safe read) and
 * `gog gmail send` (requires human approval). Both resolve to /usr/local/bin/gog.
 *
 * SOLUTION: This plugin uses the `before_tool_call` hook to rewrite read/tag
 * commands so they use the allowlisted wrapper scripts instead of raw gog.
 * Write commands are left untouched — they hit the real gog binary, which is
 * NOT in the allowlist, so exec-approval fires and Dave gets a Telegram prompt.
 *
 * FLOW:
 *   Read:  gog gmail messages search ... → gog-email-read.sh gmail messages search ...
 *          (wrapper is allowlisted → auto-approved → runs without approval)
 *
 *   Write: gog gmail send ... → unchanged
 *          (gog binary is NOT allowlisted → exec-approval fires → Dave approves)
 *
 * REQUIRES: Wrapper scripts in the allowlist (gog-email-read.sh, gog-cal-read.sh,
 * gog-email-tag.sh). The wrapper scripts validate the subcommand before executing.
 */

import type { OpenClawPluginApi } from "openclaw/plugin-sdk";
import { emptyPluginConfigSchema } from "openclaw/plugin-sdk";

const SCRIPTS_DIR = "/Users/amberives/.openclaw/workspace/scripts";

// Patterns that identify read-only email operations → route to gog-email-read.sh
const EMAIL_READ_PATTERNS = [
  /^gog\s+gmail\s+messages?\s+search\b/,
  /^gog\s+gmail\s+messages?\s+get\b/,
  /^gog\s+gmail\s+messages?\s+list\b/,
  /^gog\s+gmail\s+threads?\s+get\b/,
  /^gog\s+gmail\s+threads?\s+list\b/,
  /^gog\s+gmail\s+labels?\s+list\b/,
  /^gog\s+gmail\s+labels?\s+get\b/,
];

// Patterns that identify thread tagging → route to gog-email-tag.sh
const EMAIL_TAG_PATTERNS = [/^gog\s+gmail\s+threads?\s+modify\b/];

// Patterns that identify read-only calendar operations → route to gog-cal-read.sh
const CAL_READ_PATTERNS = [
  /^gog\s+cal\s+events?\b/,
  /^gog\s+cal\s+get\b/,
  /^gog\s+cal\s+list\b/,
];

function matchesAny(cmd: string, patterns: RegExp[]): boolean {
  return patterns.some((p) => p.test(cmd));
}

const plugin = {
  id: "gog-guard",
  name: "Gog Command Guard",
  description:
    "Routes gog read/tag commands to allowlisted wrapper scripts for auto-approval. Write commands pass through unchanged and require Dave's approval via Telegram.",
  configSchema: emptyPluginConfigSchema(),

  register(api: OpenClawPluginApi) {
    api.registerHook("before_tool_call", (event) => {
      // Only intercept exec tool calls
      if (event.toolName !== "exec") return;

      const cmd = ((event.params?.command as string) || "").trim();

      // Only care about gog commands
      if (!cmd.startsWith("gog ")) return;

      // Route read-only email ops to the allowlisted wrapper
      if (matchesAny(cmd, EMAIL_READ_PATTERNS)) {
        event.params.command = cmd.replace(
          /^gog\s+/,
          `${SCRIPTS_DIR}/gog-email-read.sh `,
        );
        return { params: event.params };
      }

      // Route thread tagging to the allowlisted wrapper
      if (matchesAny(cmd, EMAIL_TAG_PATTERNS)) {
        event.params.command = cmd.replace(
          /^gog\s+/,
          `${SCRIPTS_DIR}/gog-email-tag.sh `,
        );
        return { params: event.params };
      }

      // Route read-only calendar ops to the allowlisted wrapper
      if (matchesAny(cmd, CAL_READ_PATTERNS)) {
        event.params.command = cmd.replace(
          /^gog\s+/,
          `${SCRIPTS_DIR}/gog-cal-read.sh `,
        );
        return { params: event.params };
      }

      // Everything else (gmail send, gmail reply, cal create, etc.)
      // passes through UNCHANGED → hits /usr/local/bin/gog → NOT in allowlist
      // → triggers normal exec-approval → Dave approves via Telegram
    });

    api.logger.info(
      "[gog-guard] Loaded — reads/tags route to wrappers, writes require approval",
    );
  },
};

export default plugin;

# Rollback Baseline: Friday March 6, 2026 — 6:42 AM PT

## Status: Email System Mostly Working

As of this timestamp, the email-related changes made on March 5, 2026 are working in production. Dave has been using them and confirms "all is mostly OK."

## What's Working (Reference Point)

- Email sending via `gog gmail send --body-html` with exec-approval
- HTML formatting with `<div style="font-size:18px">` wrapper
- Standardized signature: `Amber Ives<br>MindFire, Inc.`
- Verify-with-Opus pre-send checks (`verify-with-opus.sh` / `verify-email-params.sh`)
- Threading with `--reply-to-message-id` and `--reply-all`
- Email tagging via `gog-email-tag.sh`
- Telegram draft approval workflow
- Follow-up tracker
- Heartbeat system
- Memory system (daily notes, reference files, git sync)

## Key Files at This Baseline

- `config/email.md` — Full email rules with signature, HTML enforcement, thread management
- `skills/email-send/SKILL.md` — Complete send process with verify step, recipient display, threading rules
- `memory/reference/email-style-lessons.md` — 12 lessons logged through March 5
- `memory/reference/email-formatting-rules.md` — Paragraph formatting rules
- `scripts/verify-with-opus.sh` — Opus verification script
- `scripts/verify-email-params.sh` — Bash fallback verification
- `scripts/gog-email-read.sh` — Read wrapper (safe reads without exec-approval)
- `scripts/gog-email-tag.sh` — Tag wrapper

## If We Need to Roll Back

If the MCP-native refactor (Phase 1+) breaks things, revert to this commit:
```bash
git log --oneline -5  # Find the commit closest to March 6, 2026 6:42 AM PT
git tag baseline-email-working-2026-03-06  # Tag it for easy reference
```

## What This Note Does NOT Cover

- Only email-related functionality. Calendar, Salesforce, iMessage, etc. are not yet implemented.
- The batch fix plan's machine-side changes (PATH fix, gateway restart) may or may not have been applied on Amber's machine — those are separate from the doc/config changes.

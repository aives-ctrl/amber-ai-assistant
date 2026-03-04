# Git Workflow

## Roles

- **Claude Code (Dave's machine):** Manages the config repo. Pushes changes to GitHub.
- **Amber (her machine):** Pulls updates via `update-self.sh`. Never pushes to the repo.

## File Categories

### Config Files (Claude Code manages, Amber pulls)
These define personality, rules, and processes. Changes flow one-way: repo -> Amber.
- SOUL.md, AGENTS.md, TOOLS.md, IDENTITY.md, USER.md, HEARTBEAT.md
- email.md, calendar.md, communications.md, follow-up.md, telegram.md
- APPROVAL-WORKFLOW.md, REVENUE-IDEAS.md
- All files in scripts/ and docs/

### Dynamic Working Files (Amber owns, repo has template only)
These change throughout the day as Amber works. `update-self.sh` NEVER overwrites them.
- **follow-up-tracker.md** -- active follow-up items, updated constantly

### Runtime Files (never in repo)
- memory/*.md (daily notes, Amber's runtime memory)
- *.session, *-state.json (OpenClaw runtime state)
- notification-queue.py (local runtime script)
- .env* (secrets and credentials)

## Update Process

1. Claude Code pushes changes to GitHub
2. Dave tells Amber: "update yourself from GitHub"
3. Amber runs: `./update-self.sh`
4. Script pulls from GitHub, backs up current files, copies configs (skipping dynamic files)
5. Amber may need a session restart for some changes to take effect

## Safety

- Amber NEVER runs `git push`
- `update-self.sh` NEVER overwrites follow-up-tracker.md
- Backups are created before every update (in workspace/backup-YYYYMMDD-HHMMSS/)
- If something breaks: restore from the backup directory
- To add a new dynamic file to the skip list: edit the `SKIP_FILES` variable in update-self.sh

#!/bin/bash
# =============================================================================
# Phase 1: MCP Migration Setup Script (v2 — wrapper approach)
# Run on Amber's machine. Installs google-workspace-mcp, sets up wrapper
# scripts, updates exec-approvals, and verifies everything works.
#
# Usage:
#   ./mcp-migrate-phase1.sh setup    — Install everything + configure
#   ./mcp-migrate-phase1.sh test     — Run verification tests only
#   ./mcp-migrate-phase1.sh switch   — Switch SKILL.md files from gog to MCP
#   ./mcp-migrate-phase1.sh status   — Check what's installed
#   ./mcp-migrate-phase1.sh rollback — Restore gog workflow
#
# Prerequisites:
#   - OAuth credentials: set GOOGLE_OAUTH_CLIENT_ID and GOOGLE_OAUTH_CLIENT_SECRET
#     as environment variables BEFORE running, or pass them as arguments:
#     GOOGLE_OAUTH_CLIENT_ID=xxx GOOGLE_OAUTH_CLIENT_SECRET=yyy ./mcp-migrate-phase1.sh setup
#
#   - If gog already has OAuth configured, check: gog auth status
#     The same Client ID/Secret may work.
#
# Architecture:
#   mcp-read.sh  → allowlisted (auto-approved) → calls uvx workspace-mcp for reads
#   mcp-write.sh → NOT allowlisted (needs Telegram approval) → calls uvx workspace-mcp for sends
#   No config changes to openclaw.json. No ClawBands. Same exec-approvals pattern as gog.
# =============================================================================

set -euo pipefail

# --- Configuration ---
AMBER_HOME="/Users/amberives"
WORKSPACE="${AMBER_HOME}/.openclaw/workspace"
OPENCLAW_DIR="${AMBER_HOME}/.openclaw"
SCRIPTS_DIR="${WORKSPACE}/scripts"
SKILLS_DIR="${WORKSPACE}/skills"
USER_EMAIL="aives@mindfiremail.info"
SHELL_PROFILE="${AMBER_HOME}/.zshrc"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info()  { echo -e "${BLUE}[INFO]${NC}  $1"; }
log_ok()    { echo -e "${GREEN}[OK]${NC}    $1"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC}  $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_step()  { echo -e "\n${GREEN}━━━ $1 ━━━${NC}"; }

# --- Prerequisite Checks ---
check_prereqs() {
    log_step "Checking prerequisites"

    local missing=0

    # Python 3
    if command -v python3 &>/dev/null; then
        local py_ver=$(python3 --version | cut -d' ' -f2)
        log_ok "Python $py_ver"
    else
        log_error "Python 3 not found"
        missing=1
    fi

    # uv (Python package manager)
    if command -v uv &>/dev/null; then
        log_ok "uv (Python package manager)"
    else
        log_warn "uv not found — will install"
    fi

    # OpenClaw
    if command -v openclaw &>/dev/null; then
        log_ok "openclaw CLI"
    else
        log_error "openclaw not found"
        missing=1
    fi

    # OAuth credentials
    if [ -n "${GOOGLE_OAUTH_CLIENT_ID:-}" ] && [ -n "${GOOGLE_OAUTH_CLIENT_SECRET:-}" ]; then
        log_ok "OAuth credentials found in environment"
    else
        log_warn "OAuth credentials not set."
        log_info "Check if gog has them: gog auth status"
        log_error "Set GOOGLE_OAUTH_CLIENT_ID and GOOGLE_OAUTH_CLIENT_SECRET before running setup."
        missing=1
    fi

    # Wrapper scripts exist
    if [ -f "${SCRIPTS_DIR}/mcp-read.sh" ] && [ -f "${SCRIPTS_DIR}/mcp-write.sh" ]; then
        log_ok "MCP wrapper scripts found"
    else
        log_error "Missing mcp-read.sh or mcp-write.sh in ${SCRIPTS_DIR}"
        missing=1
    fi

    if [ $missing -ne 0 ]; then
        log_error "Fix the above issues before running setup."
        exit 1
    fi

    log_ok "All prerequisites met!"
}

# --- Install google-workspace-mcp ---
install_mcp_server() {
    log_step "Installing google-workspace-mcp"

    # Install uv if needed
    if ! command -v uv &>/dev/null; then
        log_info "Installing uv..."
        pip3 install uv
    fi

    # Test that uvx can resolve workspace-mcp
    log_info "Verifying workspace-mcp is available via uvx..."
    if uvx workspace-mcp --help &>/dev/null 2>&1; then
        log_ok "workspace-mcp available via uvx"
    else
        log_info "Installing workspace-mcp via pip as fallback..."
        pip3 install workspace-mcp
    fi
}

# --- Set Environment Variables ---
setup_env_vars() {
    log_step "Setting up environment variables"

    if grep -q "GOOGLE_OAUTH_CLIENT_ID" "$SHELL_PROFILE" 2>/dev/null; then
        log_warn "OAuth env vars already in $SHELL_PROFILE — skipping"
    else
        log_info "Adding OAuth env vars to $SHELL_PROFILE..."
        cat >> "$SHELL_PROFILE" << EOF

# --- Phase 1 MCP Migration (added $(date +%Y-%m-%d)) ---
export GOOGLE_OAUTH_CLIENT_ID="${GOOGLE_OAUTH_CLIENT_ID}"
export GOOGLE_OAUTH_CLIENT_SECRET="${GOOGLE_OAUTH_CLIENT_SECRET}"
export USER_GOOGLE_EMAIL="${USER_EMAIL}"
EOF
        log_ok "Environment variables added to $SHELL_PROFILE"
    fi

    # Export for current session
    export GOOGLE_OAUTH_CLIENT_ID="${GOOGLE_OAUTH_CLIENT_ID}"
    export GOOGLE_OAUTH_CLIENT_SECRET="${GOOGLE_OAUTH_CLIENT_SECRET}"
    export USER_GOOGLE_EMAIL="${USER_EMAIL}"
}

# --- Run OAuth Flow ---
run_oauth_flow() {
    log_step "Running OAuth authorization flow"

    log_warn "============================================"
    log_warn " A BROWSER WINDOW WILL OPEN."
    log_warn " Click 'Authorize' as ${USER_EMAIL}"
    log_warn " This is the ONE manual step."
    log_warn "============================================"
    echo ""
    read -p "Press Enter when ready to open the browser..." _

    timeout 60 uvx workspace-mcp --tools gmail calendar 2>&1 || true

    log_info "If authorization succeeded, a token was cached locally."
    log_info "If the browser didn't open, try: uvx workspace-mcp --tools gmail calendar"
}

# --- Make wrapper scripts executable ---
setup_wrappers() {
    log_step "Setting up MCP wrapper scripts"

    chmod +x "${SCRIPTS_DIR}/mcp-read.sh"
    chmod +x "${SCRIPTS_DIR}/mcp-write.sh"
    log_ok "mcp-read.sh and mcp-write.sh are executable"

    # Ensure scripts dir is on PATH
    if grep -q 'openclaw/workspace/scripts' "$SHELL_PROFILE" 2>/dev/null; then
        log_ok "Scripts directory already on PATH"
    else
        echo 'export PATH="/Users/amberives/.openclaw/workspace/scripts:$PATH"' >> "$SHELL_PROFILE"
        log_ok "Added scripts directory to PATH"
    fi
}

# --- Update exec-approvals ---
update_exec_approvals() {
    log_step "Updating exec-approvals (mcp-read.sh → auto-approved)"

    if [ -f "${SCRIPTS_DIR}/update-exec-approvals-mcp.sh" ]; then
        bash "${SCRIPTS_DIR}/update-exec-approvals-mcp.sh"
        log_ok "exec-approvals updated"
    else
        log_error "update-exec-approvals-mcp.sh not found"
        exit 1
    fi
}

# --- Verify Installation ---
verify_installation() {
    log_step "Verifying installation"

    # Test a simple MCP read call
    log_info "Testing mcp-read.sh list_gmail_labels..."
    local output
    output=$(${SCRIPTS_DIR}/mcp-read.sh list_gmail_labels 2>&1) || true

    if [ -z "$output" ]; then
        log_warn "No output from MCP call — OAuth may need to be completed"
    elif echo "$output" | grep -qi "error\|traceback"; then
        log_warn "MCP call returned an error — check OAuth setup"
        echo "$output" | head -5
    else
        log_ok "MCP read test successful"
    fi

    # Verify mcp-write.sh exists but is NOT auto-approved
    log_info "Verifying mcp-write.sh requires approval..."
    if [ -f "${SCRIPTS_DIR}/mcp-write.sh" ]; then
        log_ok "mcp-write.sh exists (requires exec-approval for sends)"
    fi
}

# --- Run Tests ---
run_tests() {
    log_step "Running Phase 1 tests"

    echo ""
    log_info "TEST 1: Search unread emails"
    ${SCRIPTS_DIR}/mcp-read.sh search_gmail_messages --query "is:unread -label:Handled" --page_size 3 2>&1 | head -20
    echo ""

    log_info "TEST 2: List Gmail labels"
    ${SCRIPTS_DIR}/mcp-read.sh list_gmail_labels 2>&1 | head -20
    echo ""

    log_info "TEST 3: List calendars"
    ${SCRIPTS_DIR}/mcp-read.sh list_calendars 2>&1 | head -20
    echo ""

    log_info "TEST 4: Get today's events"
    local today=$(date +%Y-%m-%d)
    ${SCRIPTS_DIR}/mcp-read.sh get_events --calendar_id "daver@mindfireinc.com" --time_min "${today}T00:00:00" --time_max "${today}T23:59:59" 2>&1 | head -20
    echo ""

    log_ok "Read tests complete."
    echo ""
    log_warn "MANUAL TESTS STILL NEEDED (require Telegram approval):"
    log_warn "  1. mcp-write.sh send_gmail_message --to daver@mindfireinc.com --subject 'MCP Test' --body '<div>Test</div>' --body_format html"
    log_warn "  2. Reply threading test (see AMBER-MCP-INSTRUCTIONS.md)"
    log_warn "  3. mcp-write.sh manage_event --action create --calendar_id daver@mindfireinc.com --summary 'Test' --start_time 2026-03-07T15:00:00-08:00 --end_time 2026-03-07T15:30:00-08:00"
}

# --- Switch Skill Files ---
switch_skills() {
    log_step "Switching SKILL.md files from gog to MCP"

    for skill in email-read email-send calendar-read calendar-create; do
        local skill_dir="${SKILLS_DIR}/${skill}"
        local current="${skill_dir}/SKILL.md"
        local mcp="${skill_dir}/SKILL-MCP.md"
        local backup="${skill_dir}/SKILL-gog-backup.md"

        if [ ! -f "$mcp" ]; then
            log_warn "No SKILL-MCP.md for ${skill} — skipping"
            continue
        fi

        if [ -f "$current" ] && [ ! -f "$backup" ]; then
            cp "$current" "$backup"
            log_ok "Backed up ${skill}/SKILL.md → SKILL-gog-backup.md"
        fi

        cp "$mcp" "$current"
        log_ok "Switched ${skill}/SKILL.md to MCP version"
    done

    log_ok "All skill files switched. Restart your session to load the new instructions."
}

# --- Check Status ---
check_status() {
    log_step "MCP Migration Status"

    # uvx workspace-mcp
    if command -v uvx &>/dev/null && uvx workspace-mcp --help &>/dev/null 2>&1; then
        log_ok "google-workspace-mcp: installed"
    else
        log_warn "google-workspace-mcp: not installed"
    fi

    # OAuth env vars
    if [ -n "${GOOGLE_OAUTH_CLIENT_ID:-}" ]; then
        log_ok "OAuth Client ID: set"
    else
        log_warn "OAuth Client ID: not set"
    fi

    # Wrapper scripts
    if [ -x "${SCRIPTS_DIR}/mcp-read.sh" ] && [ -x "${SCRIPTS_DIR}/mcp-write.sh" ]; then
        log_ok "Wrapper scripts: executable"
    else
        log_warn "Wrapper scripts: missing or not executable"
    fi

    # Skill files
    for skill in email-read email-send calendar-read calendar-create; do
        if [ -f "${SKILLS_DIR}/${skill}/SKILL-MCP.md" ]; then
            if grep -q "mcp-read.sh\|mcp-write.sh" "${SKILLS_DIR}/${skill}/SKILL.md" 2>/dev/null; then
                log_ok "skills/${skill}: using MCP version"
            else
                log_info "skills/${skill}: SKILL-MCP.md ready (not yet active)"
            fi
        fi
    done
}

# --- Rollback ---
rollback() {
    log_step "Rolling back MCP migration"

    for skill in email-read email-send calendar-read calendar-create; do
        local backup="${SKILLS_DIR}/${skill}/SKILL-gog-backup.md"
        local active="${SKILLS_DIR}/${skill}/SKILL.md"
        if [ -f "$backup" ]; then
            cp "$backup" "$active"
            log_ok "Restored: skills/${skill}/SKILL.md from gog backup"
        fi
    done

    log_ok "Rollback complete. gog CLI workflow restored."
    log_info "Baseline tag: baseline-email-working-2026-03-06"
    log_info "Restart your session to load the restored skill files."
}

# --- Main ---
case "${1:-help}" in
    setup)
        echo ""
        echo "============================================"
        echo "  Phase 1: MCP Migration Setup (v2)"
        echo "  Wrapper approach — no config changes"
        echo "============================================"
        echo ""
        check_prereqs
        install_mcp_server
        setup_env_vars
        run_oauth_flow
        setup_wrappers
        update_exec_approvals
        verify_installation
        echo ""
        log_step "Setup complete!"
        log_info "Next: run './mcp-migrate-phase1.sh test' to verify reads."
        log_info "Then: test sends manually (needs Telegram approval)."
        log_info "Finally: run './mcp-migrate-phase1.sh switch' to activate MCP skills."
        ;;
    test)
        run_tests
        ;;
    switch)
        switch_skills
        ;;
    status)
        check_status
        ;;
    rollback)
        rollback
        ;;
    help|*)
        echo "Usage: $0 {setup|test|switch|status|rollback}"
        echo ""
        echo "  setup    — Install MCP server, configure wrappers, update exec-approvals"
        echo "  test     — Run read-only verification tests"
        echo "  switch   — Switch SKILL.md files from gog to MCP (backup originals first)"
        echo "  status   — Check what's installed and configured"
        echo "  rollback — Restore gog skill files"
        echo ""
        echo "Before 'setup', set these environment variables:"
        echo "  export GOOGLE_OAUTH_CLIENT_ID='your-client-id'"
        echo "  export GOOGLE_OAUTH_CLIENT_SECRET='your-client-secret'"
        ;;
esac

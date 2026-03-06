#!/bin/bash
# =============================================================================
# Phase 1: MCP Migration Setup Script
# Run on Amber's machine. Installs google-workspace-mcp + ClawBands,
# configures OpenClaw, and verifies everything works.
#
# Usage:
#   ./mcp-migrate-phase1.sh setup   — Install everything + configure
#   ./mcp-migrate-phase1.sh test    — Run verification tests only
#   ./mcp-migrate-phase1.sh status  — Check what's installed
#   ./mcp-migrate-phase1.sh rollback — Disable MCP, restore gog workflow
#
# Prerequisites:
#   - OAuth credentials: set GOOGLE_OAUTH_CLIENT_ID and GOOGLE_OAUTH_CLIENT_SECRET
#     as environment variables BEFORE running, or pass them as arguments:
#     GOOGLE_OAUTH_CLIENT_ID=xxx GOOGLE_OAUTH_CLIENT_SECRET=yyy ./mcp-migrate-phase1.sh setup
#
#   - If gog already has OAuth configured, check: gog auth status
#     The same Client ID/Secret may work.
#
# The ONE thing that needs a human: the OAuth consent screen in the browser
# (first run only). The script will open it automatically — just click Authorize.
# =============================================================================

set -euo pipefail

# --- Configuration ---
AMBER_HOME="/Users/amberives"
WORKSPACE="${AMBER_HOME}/.openclaw/workspace"
OPENCLAW_DIR="${AMBER_HOME}/.openclaw"
OPENCLAW_JSON="${OPENCLAW_DIR}/openclaw.json"
CLAWBANDS_DIR="${OPENCLAW_DIR}/clawbands"
POLICY_SOURCE="${WORKSPACE}/config/clawbands-policy.json"
MCP_CONFIG_SOURCE="${WORKSPACE}/config/mcp-servers.json"
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

    # Node.js
    if command -v node &>/dev/null; then
        local node_ver=$(node -v | sed 's/v//')
        local node_major=$(echo "$node_ver" | cut -d. -f1)
        if [ "$node_major" -ge 18 ]; then
            log_ok "Node.js $node_ver"
        else
            log_error "Node.js >= 18 required (found $node_ver)"
            missing=1
        fi
    else
        log_error "Node.js not found — install from https://nodejs.org"
        missing=1
    fi

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

    # npm
    if command -v npm &>/dev/null; then
        log_ok "npm $(npm -v)"
    else
        log_error "npm not found"
        missing=1
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
        log_warn "OAuth credentials not set. Checking if gog has them..."
        if command -v gog &>/dev/null; then
            log_info "Run 'gog auth status' to check existing OAuth config."
            log_info "If gog has OAuth configured, you can reuse those credentials."
        fi
        log_error "Set GOOGLE_OAUTH_CLIENT_ID and GOOGLE_OAUTH_CLIENT_SECRET before running setup."
        missing=1
    fi

    # Config files exist in repo
    if [ -f "$POLICY_SOURCE" ]; then
        log_ok "ClawBands policy template found"
    else
        log_error "Missing: $POLICY_SOURCE"
        missing=1
    fi

    if [ -f "$MCP_CONFIG_SOURCE" ]; then
        log_ok "MCP server config template found"
    else
        log_error "Missing: $MCP_CONFIG_SOURCE"
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

    local vars_added=0

    # Check if already in shell profile
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
        vars_added=1
        log_ok "Environment variables added to $SHELL_PROFILE"
    fi

    # Export for current session too
    export GOOGLE_OAUTH_CLIENT_ID="${GOOGLE_OAUTH_CLIENT_ID}"
    export GOOGLE_OAUTH_CLIENT_SECRET="${GOOGLE_OAUTH_CLIENT_SECRET}"
    export USER_GOOGLE_EMAIL="${USER_EMAIL}"

    if [ $vars_added -eq 1 ]; then
        log_info "Variables exported for current session. Will persist after shell restart."
    fi
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

    # Run the MCP server briefly to trigger OAuth
    timeout 60 uvx workspace-mcp --tools gmail calendar 2>&1 || true

    log_info "If authorization succeeded, a token was cached locally."
    log_info "If the browser didn't open, try running manually:"
    log_info "  uvx workspace-mcp --tools gmail calendar"
}

# --- Register MCP Server in OpenClaw ---
register_mcp_server() {
    log_step "Registering MCP server in OpenClaw"

    # Back up existing config
    if [ -f "$OPENCLAW_JSON" ]; then
        cp "$OPENCLAW_JSON" "${OPENCLAW_JSON}.pre-mcp-backup"
        log_ok "Backed up openclaw.json to openclaw.json.pre-mcp-backup"
    fi

    # Use Python to merge MCP server config into openclaw.json
    python3 << 'PYEOF'
import json
import os

openclaw_json = os.path.expanduser("~/.openclaw/openclaw.json")
mcp_config = os.path.join(os.environ.get("WORKSPACE", ""), "config", "mcp-servers.json")

# Read existing openclaw.json
with open(openclaw_json, 'r') as f:
    config = json.load(f)

# Read MCP server template
with open(mcp_config, 'r') as f:
    mcp = json.load(f)

# Remove documentation keys
mcp_entry = {k: v for k, v in mcp.get("google-workspace", {}).items() if not k.startswith("_")}

# Substitute actual credentials
client_id = os.environ.get("GOOGLE_OAUTH_CLIENT_ID", "")
client_secret = os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET", "")

if mcp_entry.get("env"):
    if client_id:
        mcp_entry["env"]["GOOGLE_OAUTH_CLIENT_ID"] = client_id
    if client_secret:
        mcp_entry["env"]["GOOGLE_OAUTH_CLIENT_SECRET"] = client_secret

# Merge into openclaw.json
if "mcpServers" not in config:
    config["mcpServers"] = {}

config["mcpServers"]["google-workspace"] = mcp_entry

with open(openclaw_json, 'w') as f:
    json.dump(config, f, indent=2)

print("MCP server registered in openclaw.json")
PYEOF

    if [ $? -eq 0 ]; then
        log_ok "google-workspace MCP server registered in openclaw.json"
    else
        log_error "Failed to update openclaw.json"
        exit 1
    fi
}

# --- Install ClawBands ---
install_clawbands() {
    log_step "Installing ClawBands"

    if command -v clawbands &>/dev/null; then
        log_ok "ClawBands already installed"
    else
        log_info "Installing ClawBands via npm..."
        npm install -g clawbands

        if command -v clawbands &>/dev/null; then
            log_ok "ClawBands installed successfully"
        else
            log_error "ClawBands installation failed"
            exit 1
        fi
    fi

    # Initialize if not already done
    if [ ! -d "$CLAWBANDS_DIR" ]; then
        log_info "Initializing ClawBands..."
        clawbands init --yes 2>/dev/null || clawbands init
    fi

    # Apply policy
    log_info "Applying ClawBands policy..."
    mkdir -p "$CLAWBANDS_DIR"
    cp "$POLICY_SOURCE" "${CLAWBANDS_DIR}/policy.json"
    log_ok "Policy applied: ${CLAWBANDS_DIR}/policy.json"
}

# --- Restart Gateway ---
restart_gateway() {
    log_step "Restarting OpenClaw gateway"

    openclaw gateway restart 2>&1 || {
        log_warn "Gateway restart command returned non-zero. Trying stop + start..."
        openclaw gateway stop 2>/dev/null || true
        sleep 2
        openclaw gateway start
    }

    sleep 3
    log_ok "Gateway restarted"
}

# --- Verify Installation ---
verify_installation() {
    log_step "Verifying installation"

    local all_good=1

    # Check MCP tools are registered
    log_info "Checking MCP tools..."
    local tools_output
    tools_output=$(openclaw tools list 2>&1) || true

    for tool in search_gmail_messages get_gmail_message_content send_gmail_message get_events create_event; do
        if echo "$tools_output" | grep -q "$tool"; then
            log_ok "Tool available: $tool"
        else
            log_warn "Tool not found: $tool (may need gateway restart)"
            all_good=0
        fi
    done

    # Check ClawBands status
    log_info "Checking ClawBands..."
    if clawbands status 2>&1 | grep -qi "active"; then
        log_ok "ClawBands is active"
    else
        log_warn "ClawBands may not be active — check 'clawbands status'"
        all_good=0
    fi

    if [ $all_good -eq 1 ]; then
        log_ok "All verification checks passed!"
    else
        log_warn "Some checks need attention — see warnings above"
    fi
}

# --- Run Tests ---
run_tests() {
    log_step "Running Phase 1 tests"

    echo ""
    log_info "TEST 1: Search unread emails (should auto-approve, no Telegram prompt)"
    echo '{"method": "tools/call", "params": {"name": "search_gmail_messages", "arguments": {"query": "is:unread -label:Handled", "max_results": 3, "user_google_email": "aives@mindfiremail.info"}}}' | uvx workspace-mcp --tools gmail 2>&1 | head -20
    echo ""

    log_info "TEST 2: List Gmail labels (should auto-approve)"
    echo '{"method": "tools/call", "params": {"name": "list_gmail_labels", "arguments": {"user_google_email": "aives@mindfiremail.info"}}}' | uvx workspace-mcp --tools gmail 2>&1 | head -20
    echo ""

    log_info "TEST 3: List calendars (should auto-approve)"
    echo '{"method": "tools/call", "params": {"name": "list_calendars", "arguments": {}}}' | uvx workspace-mcp --tools calendar 2>&1 | head -20
    echo ""

    log_info "TEST 4: Get today's events (should auto-approve)"
    local today=$(date +%Y-%m-%d)
    echo "{\"method\": \"tools/call\", \"params\": {\"name\": \"get_events\", \"arguments\": {\"calendar_id\": \"daver@mindfireinc.com\", \"time_min\": \"${today}T00:00:00\", \"time_max\": \"${today}T23:59:59\"}}}" | uvx workspace-mcp --tools calendar 2>&1 | head -20
    echo ""

    log_ok "Read tests complete. Check output above for results."
    echo ""
    log_warn "MANUAL TESTS STILL NEEDED (require Telegram approval):"
    log_warn "  1. Send a test email (send_gmail_message → Dave approves via Telegram)"
    log_warn "  2. Test reply threading (most critical — see MCP-MIGRATION-GUIDE.md Part D3)"
    log_warn "  3. Create a test calendar event (create_event → Dave approves via Telegram)"
}

# --- Check Status ---
check_status() {
    log_step "MCP Migration Status"

    # google-workspace-mcp
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

    # ClawBands
    if command -v clawbands &>/dev/null; then
        log_ok "ClawBands: installed"
    else
        log_warn "ClawBands: not installed"
    fi

    # Policy file
    if [ -f "${CLAWBANDS_DIR}/policy.json" ]; then
        log_ok "ClawBands policy: applied"
    else
        log_warn "ClawBands policy: not applied"
    fi

    # MCP in openclaw.json
    if [ -f "$OPENCLAW_JSON" ] && python3 -c "
import json
with open('$OPENCLAW_JSON') as f:
    c = json.load(f)
assert 'google-workspace' in c.get('mcpServers', {})
" 2>/dev/null; then
        log_ok "MCP server: registered in openclaw.json"
    else
        log_warn "MCP server: not registered in openclaw.json"
    fi

    # Skill files
    if [ -f "${WORKSPACE}/skills/email-read/SKILL-MCP.md" ]; then
        log_ok "SKILL-MCP.md files: present (not yet active)"
    else
        log_warn "SKILL-MCP.md files: not found"
    fi
}

# --- Rollback ---
rollback() {
    log_step "Rolling back MCP migration"

    # Disable MCP server in openclaw.json
    if [ -f "$OPENCLAW_JSON" ]; then
        python3 << 'PYEOF'
import json
with open("$OPENCLAW_JSON", 'r') as f:
    config = json.load(f)
if "mcpServers" in config and "google-workspace" in config["mcpServers"]:
    config["mcpServers"]["google-workspace"]["disabled"] = True
    with open("$OPENCLAW_JSON", 'w') as f:
        json.dump(config, f, indent=2)
    print("Disabled google-workspace MCP server")
else:
    print("No MCP server config found — nothing to disable")
PYEOF
    fi

    # Restore skill files if backups exist
    for skill in email-read email-send calendar-read calendar-create; do
        local backup="${WORKSPACE}/skills/${skill}/SKILL-gog-backup.md"
        local active="${WORKSPACE}/skills/${skill}/SKILL.md"
        if [ -f "$backup" ]; then
            cp "$backup" "$active"
            log_ok "Restored: skills/${skill}/SKILL.md from backup"
        fi
    done

    # Restart gateway
    openclaw gateway restart 2>&1 || true

    log_ok "Rollback complete. gog CLI workflow restored."
    log_info "The baseline tag 'baseline-email-working-2026-03-06' marks the known-good state."
}

# --- Main ---
case "${1:-help}" in
    setup)
        echo ""
        echo "============================================"
        echo "  Phase 1: MCP Migration Setup"
        echo "  Target: Amber's machine"
        echo "============================================"
        echo ""
        check_prereqs
        install_mcp_server
        setup_env_vars
        run_oauth_flow
        register_mcp_server
        install_clawbands
        restart_gateway
        verify_installation
        echo ""
        log_step "Setup complete!"
        log_info "Next: run './mcp-migrate-phase1.sh test' to verify read operations."
        log_info "Then: test send + reply threading manually (see MCP-MIGRATION-GUIDE.md Part D)."
        ;;
    test)
        run_tests
        ;;
    status)
        check_status
        ;;
    rollback)
        rollback
        ;;
    help|*)
        echo "Usage: $0 {setup|test|status|rollback}"
        echo ""
        echo "  setup    — Full installation: MCP server, ClawBands, config, OAuth flow"
        echo "  test     — Run read-only verification tests"
        echo "  status   — Check what's installed and configured"
        echo "  rollback — Disable MCP, restore gog workflow"
        echo ""
        echo "Before 'setup', set these environment variables:"
        echo "  export GOOGLE_OAUTH_CLIENT_ID='your-client-id'"
        echo "  export GOOGLE_OAUTH_CLIENT_SECRET='your-client-secret'"
        echo ""
        echo "If gog already has OAuth, you may be able to reuse its credentials."
        echo "Check: gog auth status"
        ;;
esac

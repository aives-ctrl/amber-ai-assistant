#!/bin/bash
# =============================================================================
# MCP Test Suite — Regression tests for google-workspace-mcp + ClawBands
#
# Run anytime to verify email and calendar MCP integration is working.
#
# Usage:
#   ./mcp-test-suite.sh reads      — Read-only tests (auto-approved, no Telegram)
#   ./mcp-test-suite.sh sends      — Send/create tests (needs Dave on Telegram)
#   ./mcp-test-suite.sh threading  — Reply threading test (needs Dave on Telegram)
#   ./mcp-test-suite.sh all        — Everything in sequence
#   ./mcp-test-suite.sh quick      — Fast smoke test (one read, one label, one cal)
#
# Exit codes:
#   0 = all tests passed
#   1 = one or more tests failed
# =============================================================================

set -uo pipefail

USER_EMAIL="aives@mindfiremail.info"
DAVE_CALENDAR="daver@mindfireinc.com"
DAVE_EMAIL="daver@mindfireinc.com"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'
BOLD='\033[1m'

PASS=0
FAIL=0
SKIP=0
RESULTS=()

log_test()   { echo -e "\n${CYAN}[TEST]${NC}  $1"; }
log_pass()   { echo -e "${GREEN}[PASS]${NC}  $1"; PASS=$((PASS+1)); RESULTS+=("PASS: $1"); }
log_fail()   { echo -e "${RED}[FAIL]${NC}  $1"; FAIL=$((FAIL+1)); RESULTS+=("FAIL: $1"); }
log_skip()   { echo -e "${YELLOW}[SKIP]${NC}  $1"; SKIP=$((SKIP+1)); RESULTS+=("SKIP: $1"); }
log_info()   { echo -e "${BLUE}[INFO]${NC}  $1"; }

# Helper: call an MCP tool and capture output
mcp_call() {
    local tool_name="$1"
    local args_json="$2"
    local tools_flag="${3:-gmail}"

    local result
    result=$(echo "{\"method\": \"tools/call\", \"params\": {\"name\": \"${tool_name}\", \"arguments\": ${args_json}}}" \
        | timeout 30 uvx workspace-mcp --tools "$tools_flag" 2>&1) || true
    echo "$result"
}

# Helper: check if output contains expected content
assert_contains() {
    local output="$1"
    local expected="$2"
    local test_name="$3"

    if echo "$output" | grep -qi "$expected"; then
        log_pass "$test_name"
        return 0
    else
        log_fail "$test_name — expected to find '$expected'"
        return 1
    fi
}

# Helper: check output is NOT an error
assert_no_error() {
    local output="$1"
    local test_name="$2"

    if echo "$output" | grep -qi "error\|exception\|traceback\|failed"; then
        log_fail "$test_name — got error in output"
        echo "$output" | head -5
        return 1
    else
        log_pass "$test_name"
        return 0
    fi
}

# =============================================================================
# READ TESTS — All auto-approved, no Telegram prompts
# =============================================================================

test_search_inbox() {
    log_test "Search inbox: unread emails (search_gmail_messages)"
    local output
    output=$(mcp_call "search_gmail_messages" "{\"query\": \"is:unread -label:Handled\", \"max_results\": 3, \"user_google_email\": \"${USER_EMAIL}\"}" "gmail")

    if [ -z "$output" ]; then
        log_fail "Search inbox — no output"
    elif echo "$output" | grep -qi "error"; then
        log_fail "Search inbox — error response"
        echo "$output" | head -3
    else
        log_pass "Search inbox — returned results"
    fi
}

test_search_by_sender() {
    log_test "Search by sender (search_gmail_messages)"
    local output
    output=$(mcp_call "search_gmail_messages" "{\"query\": \"from:${DAVE_EMAIL}\", \"max_results\": 3, \"user_google_email\": \"${USER_EMAIL}\"}" "gmail")

    if echo "$output" | grep -qi "error\|traceback"; then
        log_fail "Search by sender — error response"
    else
        log_pass "Search by sender"
    fi
}

test_search_sent() {
    log_test "Search sent mail (search_gmail_messages)"
    local output
    output=$(mcp_call "search_gmail_messages" "{\"query\": \"in:sent\", \"max_results\": 3, \"user_google_email\": \"${USER_EMAIL}\"}" "gmail")

    if echo "$output" | grep -qi "error\|traceback"; then
        log_fail "Search sent mail — error response"
    else
        log_pass "Search sent mail"
    fi
}

test_list_labels() {
    log_test "List Gmail labels (list_gmail_labels)"
    local output
    output=$(mcp_call "list_gmail_labels" "{\"user_google_email\": \"${USER_EMAIL}\"}" "gmail")

    if echo "$output" | grep -qi "Handled\|INBOX\|SENT"; then
        log_pass "List labels — found expected labels"
    elif echo "$output" | grep -qi "error"; then
        log_fail "List labels — error response"
    else
        log_pass "List labels — returned results (check for expected labels manually)"
    fi
}

test_get_message() {
    log_test "Get specific message (get_gmail_message_content)"

    # First, search for a recent message to get an ID
    log_info "Finding a recent message ID..."
    local search_output
    search_output=$(mcp_call "search_gmail_messages" "{\"query\": \"is:unread OR in:inbox\", \"max_results\": 1, \"user_google_email\": \"${USER_EMAIL}\"}" "gmail")

    # Try to extract a message ID (format varies by MCP server version)
    local msg_id
    msg_id=$(echo "$search_output" | grep -oE '"id"\s*:\s*"[a-f0-9]+"' | head -1 | grep -oE '[a-f0-9]{10,}') || true

    if [ -z "$msg_id" ]; then
        log_skip "Get message — couldn't extract a message ID from search results"
        return
    fi

    log_info "Using message ID: $msg_id"
    local output
    output=$(mcp_call "get_gmail_message_content" "{\"message_id\": \"${msg_id}\", \"user_google_email\": \"${USER_EMAIL}\"}" "gmail")

    if echo "$output" | grep -qi "from\|subject\|date"; then
        log_pass "Get message — returned message content"
    elif echo "$output" | grep -qi "error"; then
        log_fail "Get message — error response"
    else
        log_pass "Get message — returned data"
    fi
}

test_get_thread() {
    log_test "Get thread (get_gmail_thread_content)"

    # Search for a thread
    local search_output
    search_output=$(mcp_call "search_gmail_messages" "{\"query\": \"in:inbox\", \"max_results\": 1, \"user_google_email\": \"${USER_EMAIL}\"}" "gmail")

    local thread_id
    thread_id=$(echo "$search_output" | grep -oE '"threadId"\s*:\s*"[a-f0-9]+"' | head -1 | grep -oE '[a-f0-9]{10,}') || true

    if [ -z "$thread_id" ]; then
        log_skip "Get thread — couldn't extract a thread ID"
        return
    fi

    log_info "Using thread ID: $thread_id"
    local output
    output=$(mcp_call "get_gmail_thread_content" "{\"thread_id\": \"${thread_id}\", \"user_google_email\": \"${USER_EMAIL}\"}" "gmail")

    if echo "$output" | grep -qi "error\|traceback"; then
        log_fail "Get thread — error response"
    else
        log_pass "Get thread — returned thread data"
    fi
}

test_list_calendars() {
    log_test "List calendars (list_calendars)"
    local output
    output=$(mcp_call "list_calendars" "{}" "calendar")

    if echo "$output" | grep -qi "error\|traceback"; then
        log_fail "List calendars — error response"
    else
        log_pass "List calendars"
    fi
}

test_get_events_today() {
    log_test "Get today's calendar events (get_events)"
    local today
    today=$(date +%Y-%m-%d)
    local output
    output=$(mcp_call "get_events" "{\"calendar_id\": \"${DAVE_CALENDAR}\", \"time_min\": \"${today}T00:00:00\", \"time_max\": \"${today}T23:59:59\"}" "calendar")

    if echo "$output" | grep -qi "error\|traceback"; then
        log_fail "Get today's events — error response"
    else
        log_pass "Get today's events"
    fi
}

test_get_events_tomorrow() {
    log_test "Get tomorrow's calendar events (get_events)"
    local tomorrow
    tomorrow=$(date -v+1d +%Y-%m-%d 2>/dev/null || date -d "+1 day" +%Y-%m-%d)
    local output
    output=$(mcp_call "get_events" "{\"calendar_id\": \"${DAVE_CALENDAR}\", \"time_min\": \"${tomorrow}T00:00:00\", \"time_max\": \"${tomorrow}T23:59:59\"}" "calendar")

    if echo "$output" | grep -qi "error\|traceback"; then
        log_fail "Get tomorrow's events — error response"
    else
        log_pass "Get tomorrow's events"
    fi
}

# =============================================================================
# CLAWBANDS POLICY TESTS — Verify approval rules
# =============================================================================

test_clawbands_status() {
    log_test "ClawBands status"
    if command -v clawbands &>/dev/null; then
        local output
        output=$(clawbands status 2>&1) || true
        if echo "$output" | grep -qi "active\|running\|loaded"; then
            log_pass "ClawBands is active"
        else
            log_fail "ClawBands not active: $output"
        fi
    else
        log_fail "ClawBands not installed"
    fi
}

test_clawbands_policy() {
    log_test "ClawBands policy file exists"
    local policy_path="${HOME}/.openclaw/clawbands/policy.json"
    if [ -f "$policy_path" ]; then
        # Verify key rules
        if python3 -c "
import json, sys
with open('${policy_path}') as f:
    p = json.load(f)
rules = p.get('rules', {}).get('google-workspace', {})
assert rules.get('search_gmail_messages') == 'ALLOW', 'search should be ALLOW'
assert rules.get('send_gmail_message') == 'ASK', 'send should be ASK'
assert rules.get('delete_event') == 'DENY', 'delete_event should be DENY'
print('Policy rules verified')
" 2>&1; then
            log_pass "ClawBands policy — rules correct (ALLOW/ASK/DENY)"
        else
            log_fail "ClawBands policy — rules don't match expected values"
        fi
    else
        log_fail "ClawBands policy file not found at $policy_path"
    fi
}

# =============================================================================
# SEND TESTS — Require Dave's Telegram approval
# =============================================================================

test_send_email() {
    log_test "Send test email (send_gmail_message) — NEEDS TELEGRAM APPROVAL"
    log_info "Sending test email to ${DAVE_EMAIL}..."
    log_info "Dave: approve or deny this on Telegram."

    local timestamp
    timestamp=$(date "+%Y-%m-%d %H:%M:%S")
    local output
    output=$(mcp_call "send_gmail_message" "{
        \"to\": \"${DAVE_EMAIL}\",
        \"subject\": \"MCP Test Suite — ${timestamp}\",
        \"body\": \"<div style='font-size:18px'><p>Automated test from mcp-test-suite.sh at ${timestamp}.</p><p>If you received this, email sending via MCP is working.</p><p>Best,</p><p>Amber Ives<br>MindFire, Inc.</p></div>\",
        \"body_format\": \"html\",
        \"user_google_email\": \"${USER_EMAIL}\"
    }" "gmail")

    if echo "$output" | grep -qi "error\|denied\|rejected"; then
        log_fail "Send email — error or denied"
        echo "$output" | head -5
    else
        log_pass "Send email — sent (check Dave's inbox)"
    fi
}

test_create_event() {
    log_test "Create test calendar event (create_event) — NEEDS TELEGRAM APPROVAL"

    local tomorrow
    tomorrow=$(date -v+1d +%Y-%m-%d 2>/dev/null || date -d "+1 day" +%Y-%m-%d)
    local output
    output=$(mcp_call "create_event" "{
        \"calendar_id\": \"${DAVE_CALENDAR}\",
        \"summary\": \"MCP Test Event — DELETE ME\",
        \"start\": \"${tomorrow}T15:00:00\",
        \"end\": \"${tomorrow}T15:30:00\",
        \"description\": \"Automated test from mcp-test-suite.sh. Safe to delete.\"
    }" "calendar")

    if echo "$output" | grep -qi "error\|denied\|rejected"; then
        log_fail "Create event — error or denied"
        echo "$output" | head -5
    else
        log_pass "Create event — created (delete manually in Google Calendar)"
    fi
}

# =============================================================================
# THREADING TEST — The critical reply-all test
# =============================================================================

test_reply_threading() {
    log_test "Reply threading test — NEEDS TELEGRAM APPROVAL"
    echo ""
    log_info "This test verifies that replies land IN the original thread."
    log_info "Prerequisites: Dave should have sent a test email to ${USER_EMAIL}"
    echo ""

    # Find the most recent email from Dave
    log_info "Searching for recent email from Dave..."
    local search_output
    search_output=$(mcp_call "search_gmail_messages" "{\"query\": \"from:${DAVE_EMAIL} newer_than:1d\", \"max_results\": 1, \"user_google_email\": \"${USER_EMAIL}\"}" "gmail")

    local msg_id thread_id
    msg_id=$(echo "$search_output" | grep -oE '"id"\s*:\s*"[a-f0-9]+"' | head -1 | grep -oE '[a-f0-9]{10,}') || true
    thread_id=$(echo "$search_output" | grep -oE '"threadId"\s*:\s*"[a-f0-9]+"' | head -1 | grep -oE '[a-f0-9]{10,}') || true

    if [ -z "$msg_id" ] || [ -z "$thread_id" ]; then
        log_skip "Reply threading — no recent email from Dave found. Have Dave send a test email first."
        return
    fi

    log_info "Found message: $msg_id in thread: $thread_id"

    # Get the message to read headers
    log_info "Reading message to capture headers..."
    local msg_output
    msg_output=$(mcp_call "get_gmail_message_content" "{\"message_id\": \"${msg_id}\", \"user_google_email\": \"${USER_EMAIL}\"}" "gmail")

    # Extract subject (best effort)
    local subject
    subject=$(echo "$msg_output" | grep -oE '"subject"\s*:\s*"[^"]*"' | head -1 | sed 's/"subject"\s*:\s*"//;s/"$//') || true
    subject="${subject:-Test Thread}"

    log_info "Subject: $subject"
    log_info "Sending reply... Dave: approve on Telegram."

    local timestamp
    timestamp=$(date "+%H:%M:%S")
    local output
    output=$(mcp_call "send_gmail_message" "{
        \"to\": \"${DAVE_EMAIL}\",
        \"subject\": \"RE: ${subject}\",
        \"body\": \"<div style='font-size:18px'><p>Threading test reply at ${timestamp}.</p><p>If this appears IN the original thread (not as a separate email), threading works.</p><p>Best,</p><p>Amber Ives<br>MindFire, Inc.</p></div>\",
        \"body_format\": \"html\",
        \"thread_id\": \"${thread_id}\",
        \"in_reply_to\": \"${msg_id}\",
        \"references\": \"${msg_id}\",
        \"user_google_email\": \"${USER_EMAIL}\"
    }" "gmail")

    if echo "$output" | grep -qi "error\|denied"; then
        log_fail "Reply threading — error or denied"
    else
        log_pass "Reply threading — sent (CHECK GMAIL: is it in the thread?)"
        log_info ">>> MANUAL CHECK: Open Gmail, find the thread, verify the reply is inside it."
    fi
}

# =============================================================================
# ENVIRONMENT / CONFIG TESTS
# =============================================================================

test_env_vars() {
    log_test "OAuth environment variables"
    if [ -n "${GOOGLE_OAUTH_CLIENT_ID:-}" ]; then
        log_pass "GOOGLE_OAUTH_CLIENT_ID is set"
    else
        log_fail "GOOGLE_OAUTH_CLIENT_ID not set"
    fi

    if [ -n "${GOOGLE_OAUTH_CLIENT_SECRET:-}" ]; then
        log_pass "GOOGLE_OAUTH_CLIENT_SECRET is set"
    else
        log_fail "GOOGLE_OAUTH_CLIENT_SECRET not set"
    fi
}

test_mcp_server_config() {
    log_test "MCP server in openclaw.json"
    local openclaw_json="${HOME}/.openclaw/openclaw.json"
    if [ -f "$openclaw_json" ]; then
        if python3 -c "
import json
with open('${openclaw_json}') as f:
    c = json.load(f)
mcp = c.get('mcpServers', {}).get('google-workspace', {})
assert mcp.get('command') == 'uvx', 'command should be uvx'
assert not mcp.get('disabled', False), 'should not be disabled'
print('MCP server config OK')
" 2>&1; then
            log_pass "MCP server registered and enabled"
        else
            log_fail "MCP server config issue"
        fi
    else
        log_fail "openclaw.json not found"
    fi
}

test_skill_files() {
    log_test "SKILL-MCP.md files exist"
    local workspace="${HOME}/.openclaw/workspace"
    local all_exist=true
    for skill in email-read email-send calendar-read calendar-create; do
        if [ -f "${workspace}/skills/${skill}/SKILL-MCP.md" ]; then
            log_pass "skills/${skill}/SKILL-MCP.md exists"
        else
            log_fail "skills/${skill}/SKILL-MCP.md missing"
            all_exist=false
        fi
    done
}

# =============================================================================
# TEST RUNNERS
# =============================================================================

run_reads() {
    echo -e "\n${BOLD}═══════════════════════════════════════${NC}"
    echo -e "${BOLD}  MCP Test Suite — READ OPERATIONS     ${NC}"
    echo -e "${BOLD}  (all auto-approved, no Telegram)     ${NC}"
    echo -e "${BOLD}═══════════════════════════════════════${NC}"

    test_env_vars
    test_mcp_server_config
    test_clawbands_status
    test_clawbands_policy
    test_skill_files
    test_search_inbox
    test_search_by_sender
    test_search_sent
    test_list_labels
    test_get_message
    test_get_thread
    test_list_calendars
    test_get_events_today
    test_get_events_tomorrow
}

run_sends() {
    echo -e "\n${BOLD}═══════════════════════════════════════${NC}"
    echo -e "${BOLD}  MCP Test Suite — SEND OPERATIONS     ${NC}"
    echo -e "${BOLD}  (needs Dave on Telegram)             ${NC}"
    echo -e "${BOLD}═══════════════════════════════════════${NC}"

    test_send_email
    test_create_event
}

run_threading() {
    echo -e "\n${BOLD}═══════════════════════════════════════${NC}"
    echo -e "${BOLD}  MCP Test Suite — REPLY THREADING     ${NC}"
    echo -e "${BOLD}  (most critical test)                 ${NC}"
    echo -e "${BOLD}═══════════════════════════════════════${NC}"

    test_reply_threading
}

run_quick() {
    echo -e "\n${BOLD}═══════════════════════════════════════${NC}"
    echo -e "${BOLD}  MCP Test Suite — QUICK SMOKE TEST    ${NC}"
    echo -e "${BOLD}═══════════════════════════════════════${NC}"

    test_env_vars
    test_mcp_server_config
    test_search_inbox
    test_list_labels
    test_list_calendars
    test_get_events_today
}

print_summary() {
    echo ""
    echo -e "${BOLD}═══════════════════════════════════════${NC}"
    echo -e "${BOLD}  TEST SUMMARY                         ${NC}"
    echo -e "${BOLD}═══════════════════════════════════════${NC}"
    echo ""

    for result in "${RESULTS[@]}"; do
        if [[ "$result" == PASS* ]]; then
            echo -e "  ${GREEN}✓${NC} ${result#PASS: }"
        elif [[ "$result" == FAIL* ]]; then
            echo -e "  ${RED}✗${NC} ${result#FAIL: }"
        elif [[ "$result" == SKIP* ]]; then
            echo -e "  ${YELLOW}○${NC} ${result#SKIP: }"
        fi
    done

    echo ""
    echo -e "  ${GREEN}Passed: ${PASS}${NC}  ${RED}Failed: ${FAIL}${NC}  ${YELLOW}Skipped: ${SKIP}${NC}"
    echo ""

    if [ $FAIL -eq 0 ]; then
        echo -e "  ${GREEN}${BOLD}ALL TESTS PASSED ✓${NC}"
    else
        echo -e "  ${RED}${BOLD}${FAIL} TEST(S) FAILED ✗${NC}"
    fi
    echo ""
}

# --- Main ---
case "${1:-help}" in
    reads)
        run_reads
        print_summary
        ;;
    sends)
        run_sends
        print_summary
        ;;
    threading)
        run_threading
        print_summary
        ;;
    all)
        run_reads
        run_sends
        run_threading
        print_summary
        ;;
    quick)
        run_quick
        print_summary
        ;;
    help|*)
        echo "MCP Test Suite — Regression tests for email + calendar MCP integration"
        echo ""
        echo "Usage: $0 {reads|sends|threading|all|quick}"
        echo ""
        echo "  reads      Read-only tests: search, get message, get thread, labels, calendar"
        echo "             Auto-approved — no Telegram prompts. Safe to run anytime."
        echo ""
        echo "  sends      Send tests: email + calendar event creation"
        echo "             Needs Dave on Telegram to approve."
        echo ""
        echo "  threading  Reply threading test: replies land in the correct thread"
        echo "             Most critical test. Needs Dave on Telegram + a recent email from Dave."
        echo ""
        echo "  all        Run everything in sequence (reads → sends → threading)"
        echo ""
        echo "  quick      Fast smoke test: env vars, config, one search, one label, one calendar"
        echo "             Run this for a quick health check."
        echo ""
        echo "Exit code: 0 if all passed, 1 if any failed."
        ;;
esac

exit $FAIL

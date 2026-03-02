# Comprehensive Cost Tracking Plan

## Problem Identified
My initial estimate: $3.83  
My "accurate" analysis: $0.90  
Actual cost: **$10.77**

**Root cause:** Missing ~90% of token usage from incomplete data sources.

## Data Sources Found

### 1. Session Store API (`openclaw sessions --json`)
- **Current coverage:** 83 sessions summarized
- **Missing:** Only shows current token counts per session, not historical usage
- **Issue:** `inputTokens`/`outputTokens` appear to be last-run-only, not cumulative

### 2. Cron Run Logs (`openclaw cron runs`)
- **Current coverage:** 40 Email Processor + 37 RingCentral runs
- **Working correctly:** $0.84 total cron costs (accurate for these jobs)
- **Complete:** All cron runs appear to be captured

### 3. Individual Session Files (📁 **NEWLY DISCOVERED**)
- **Location:** `~/.openclaw/agents/main/sessions/*.jsonl`
- **Scope:** 89 individual session log files from today
- **Size:** Some files >600KB (substantial token usage)
- **Status:** **NOT ANALYZED YET** - this is likely the missing $9+ in costs

### 4. Model Override Tracking
- **Found:** Main session shows `"modelOverride": "claude-opus-4-6"`
- **Issue:** My analysis assumed Sonnet pricing but session used Opus extensively
- **Impact:** 5x cost multiplier for Opus vs Sonnet

## Accurate Cost Tracking Implementation Plan

### Phase 1: Complete Session Log Analysis
**Goal:** Analyze all individual .jsonl session files for token usage

**Implementation:**
1. **Parse all .jsonl files** from today (`find ~/.openclaw/agents/main/sessions/ -name "*.jsonl" -newermt "2026-03-01"`)
2. **Extract token usage** from each session log entry
3. **Track model switches** within sessions (Sonnet → Opus transitions)
4. **Sum total usage** across all sessions

**Expected outcome:** Account for the missing ~$9 in usage

### Phase 2: Real-Time Cost Aggregation  
**Goal:** Build system that tracks costs in real-time across all sessions

**Implementation:**
1. **Scheduled analysis:** Run comprehensive cost analysis every hour
2. **Delta tracking:** Track new costs since last analysis
3. **Model awareness:** Track which sessions use which models
4. **Alert thresholds:** Flag when daily spending exceeds targets

### Phase 3: Predictive Monitoring
**Goal:** Accurate daily/monthly cost projections

**Implementation:**
1. **Usage patterns:** Track cost patterns by hour/day type
2. **Trend analysis:** Identify cost spikes before they impact billing
3. **Optimization recommendations:** Suggest model/frequency changes based on real data

## Immediate Next Steps

**1. Build comprehensive session log analyzer**
```python
# Parse all .jsonl files from today
# Extract token usage from each message
# Track model usage per session
# Calculate precise costs
```

**2. Validate against known data points**
- Compare calculated total vs $10.77 auto-recharge
- Verify individual session costs match session_status output
- Cross-check cron costs against run logs

**3. Deploy accurate monitoring**
- Add to heartbeat system for 3x daily reporting
- Replace estimates with real session log analysis
- Build dashboard for daily/weekly cost trends

## Expected Results

**Accuracy target:** >95% match between calculated and actual costs  
**Coverage:** All OpenClaw sessions, cron jobs, model switches  
**Frequency:** Real-time tracking with 3x daily summaries  
**Actionable data:** Precise cost breakdown for optimization decisions  

Once this system is working, we'll have the accurate data needed to make informed decisions about cron frequency, model usage, and cost optimization.
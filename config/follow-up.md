# FOLLOW-UP.md - Email Follow-up Tracking & Rules

## Current Follow-up Status

**Currently tracking in `follow-up-tracker.md`:**

### PREMATURE Follow-ups (MISTAKE - Too Early)
- **Chris Lien (BCC Software)** - sent 2026-02-28 (should have waited until 2026-03-04)
- **Tiffany Todd (USPS)** - sent 2026-02-28 (should have waited until 2026-03-04)  
- **Status:** MISTAKE - both sent only 1 day after original emails instead of 3 business days

### DSCOOP Meeting Coordination (Pending)
- **Glen Adams (HP)** - sent 2026-02-28, follow-up due 2026-03-05
- **Peter van Teeseling (DSCOOP)** - sent 2026-02-28, follow-up due 2026-03-05
- **Status:** PENDING - within appropriate timeline

## Follow-up Timing Rules

### 3-Day Business Rule (Default)
- **DEFAULT:** 3 business days for all follow-ups unless otherwise specified
- **Business days only:** Monday-Friday count, weekends don't count
- **Example:** Email sent Friday = Follow up Wednesday (Mon=day1, Tue=day2, Wed=day3)

### Before Sending Follow-ups
1. **ALWAYS check original send date first** - look up the actual email timestamp
2. **Calculate 3 business days** from original send date (not from when I notice it's missing)
3. **Only follow up if deadline has passed**
4. **Draft follow-up and get Dave's approval** (same rule as all external emails)

## Follow-up Tracking System

### Location: `follow-up-tracker.md`
- **Add ALL outbound emails** requiring responses to this tracker
- **Track:** Who, when sent, what asking for, follow-up due date, status
- **Check during heartbeats:** Look for overdue follow-ups twice daily
- **Update status:** When responses received or additional follow-ups sent

### Follow-up Categories
- **PENDING:** Within timeline, waiting for response
- **OVERDUE:** Past 3 business days, needs follow-up  
- **RESPONDED:** Response received, moved to completed section
- **ESCALATED:** Multiple follow-ups sent, may need different approach

## Follow-up Content Guidelines

### Follow-up Email Approach
- **Reference original request** briefly
- **Restate what you're asking for** clearly  
- **Maintain friendly, professional tone**
- **Keep to 5-sentence max** (same brevity rule)
- **Don't be pushy** - just professionally persistent

### Escalation Timeline
- **First follow-up:** 3 business days after original
- **Second follow-up:** 1 week after first follow-up
- **After second follow-up:** Discuss with Dave about next steps

## Integration with Other Systems

### Heartbeat Integration (per HEARTBEAT.md)
- Every heartbeat during business hours, scan follow-up-tracker.md for overdue items
- Before alerting Dave, first check inbox for responses that might have been missed
- Present overdue items in Telegram with: who, what topic, days overdue, proposed follow-up draft
- Update tracker immediately when responses are found

### Auto-Detection of New Follow-Up Items
- When processing incoming emails, automatically detect items that need follow-up
- If Dave is CC'd on an email exchange that implies a pending response, add to tracker
- When an email says "I'll get back to you by [date]," add a tracker entry with that date
- When Amber sends an email expecting a response, add to tracker immediately

### Friday Afternoon Summary (Weekly)
- Compile all pending follow-ups for the week
- Present to Dave via Telegram: what's resolved, what's still pending, what needs escalation
- Clean up completed items (move to Completed section in tracker)

### Notification Queue Integration
- **Overdue follow-ups:** Medium priority notification to Dave
- **Important follow-ups (DSCOOP, key clients):** High priority notification
- **Multiple missed follow-ups:** High priority - may need escalation discussion

## Common Follow-up Mistakes to Avoid
- Don't send follow-ups too early (check original date first!)
- Don't send follow-ups without drafting and approval first
- Don't follow up multiple times in same week unless urgent
- Don't forget to update tracker when responses come in
- Don't let items sit overdue without alerting Dave

## Special Cases
- **Event coordination (DSCOOP, meetings):** May follow up more aggressively as event approaches
- **Time-sensitive requests:** Shorter follow-up window (1-2 business days)
- **Vendor/service providers:** Standard 3-day rule applies
- **Internal MindFire team:** May be more casual, but still track
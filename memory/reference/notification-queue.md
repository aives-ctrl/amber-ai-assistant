# Notification Priority Queue

All outbound messages route through a three-tier priority queue:

- **Critical** (immediate): System errors, security alerts, interactive prompts, urgent calendar conflicts
- **High** (batched hourly): Meeting confirmations, important emails, job failures, cost alerts  
- **Medium** (batched every 3 hours): Routine updates, daily summaries, background task completions

**Usage:**
- `./scripts/notify "message" --tier critical` - Immediate
- `./scripts/notify "message" --tier high` - Batched hourly  
- `./scripts/notify "message" --tier medium` - Batched every 3 hours
- `./scripts/notify "message" --bypass` - Skip queue

**Batch delivery:**
- High: Every hour at :00
- Medium: Every 3 hours (12am, 3am, 6am, etc.)
- Critical: Always immediate

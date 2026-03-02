#!/usr/bin/env python3
"""
Notification Priority Queue Manager
Handles three-tier notification batching to reduce alert fatigue
"""

import sqlite3
import json
import sys
import datetime
import re
import subprocess
import os
from typing import Literal, Optional, List, Dict, Any

DB_PATH = "/Users/amberives/.openclaw/workspace/notification-queue.db"
CONFIG_PATH = "/Users/amberives/.openclaw/workspace/notification-config.json"

TierType = Literal["critical", "high", "medium"]
StatusType = Literal["pending", "delivered", "failed"]

def load_config() -> Dict[str, Any]:
    """Load notification configuration"""
    with open(CONFIG_PATH) as f:
        return json.load(f)

def classify_message(message: str, source: str = "", context: Dict = None) -> TierType:
    """Classify message into priority tier"""
    config = load_config()
    
    message_lower = message.lower()
    
    # Check for critical keywords
    for keyword in config["classification_rules"]["keywords"]["critical"]:
        if keyword in message_lower:
            return "critical"
    
    # Check critical sources
    if source in config["classification_rules"]["sources"]["critical"]:
        return "critical"
    
    # Check for high priority keywords
    for keyword in config["classification_rules"]["keywords"]["high"]:
        if keyword in message_lower:
            return "high"
    
    # Check high priority sources
    if source in config["classification_rules"]["sources"]["high"]:
        return "high"
    
    # Default to medium
    return "medium"

def add_to_queue(
    message: str, 
    channel: str = "telegram",
    target: str = None,
    tier: TierType = None,
    source: str = "",
    context: Dict = None,
    bypass: bool = False
) -> int:
    """Add message to notification queue"""
    
    # If bypass is True, send immediately
    if bypass:
        return send_immediate(message, channel, target)
    
    # Classify if tier not provided
    if tier is None:
        tier = classify_message(message, source, context)
    
    # Calculate scheduled delivery time
    now = datetime.datetime.now()
    if tier == "critical":
        scheduled_for = now  # Immediate
    elif tier == "high":
        # Next hour boundary
        scheduled_for = now.replace(minute=0, second=0, microsecond=0) + datetime.timedelta(hours=1)
    else:  # medium
        # Next 3-hour boundary
        hour = (now.hour // 3 + 1) * 3
        scheduled_for = now.replace(hour=hour % 24, minute=0, second=0, microsecond=0)
        if hour >= 24:
            scheduled_for += datetime.timedelta(days=1)
    
    # Insert into queue
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO queue (tier, channel, target, message, scheduled_for, context)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (tier, channel, target, message, scheduled_for.isoformat(), json.dumps(context or {})))
        
        message_id = cursor.lastrowid
    
    # If critical, deliver immediately
    if tier == "critical":
        deliver_message(message_id)
    
    return message_id

def send_immediate(message: str, channel: str, target: str = None) -> int:
    """Send message immediately, bypassing queue"""
    if channel == "telegram":
        # Use OpenClaw message tool or direct API call
        subprocess.run([
            "curl", "-X", "POST", 
            f"https://api.telegram.org/bot8285559457:AAEbQlSuVvzXfSt9uEuai_GyWSNLWf1eyuM/sendMessage",
            "-d", f"chat_id=8703088279",
            "-d", f"text={message}"
        ], capture_output=True)
    return 0

def deliver_message(message_id: int) -> bool:
    """Deliver a specific message"""
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get message details
        cursor.execute("SELECT * FROM queue WHERE id = ? AND status = 'pending'", (message_id,))
        row = cursor.fetchone()
        
        if not row:
            return False
        
        # Attempt delivery
        success = send_immediate(row['message'], row['channel'], row['target'])
        
        # Update status
        if success == 0:
            cursor.execute("""
                UPDATE queue SET status = 'delivered', delivered_at = CURRENT_TIMESTAMP 
                WHERE id = ?
            """, (message_id,))
            return True
        else:
            cursor.execute("""
                UPDATE queue SET retry_count = retry_count + 1 
                WHERE id = ?
            """, (message_id,))
            return False

def flush_batch(tier: TierType) -> List[Dict]:
    """Flush all pending messages of a specific tier"""
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get pending messages for this tier that are ready to send
        now = datetime.datetime.now().isoformat()
        cursor.execute("""
            SELECT * FROM queue 
            WHERE tier = ? AND status = 'pending' AND scheduled_for <= ?
            ORDER BY created_at
        """, (tier, now))
        
        messages = cursor.fetchall()
        results = []
        
        if messages:
            # Group messages by channel for digest format
            grouped = {}
            for msg in messages:
                channel = msg['channel']
                if channel not in grouped:
                    grouped[channel] = []
                grouped[channel].append(msg)
            
            # Send digest for each channel
            for channel, msgs in grouped.items():
                if len(msgs) == 1:
                    # Single message, send as-is
                    success = deliver_message(msgs[0]['id'])
                    results.append({"id": msgs[0]['id'], "success": success})
                else:
                    # Multiple messages, create digest
                    digest = create_digest(msgs, tier)
                    # Send digest and mark all as delivered
                    success = send_immediate(digest, channel)
                    for msg in msgs:
                        if success == 0:
                            cursor.execute("""
                                UPDATE queue SET status = 'delivered', delivered_at = CURRENT_TIMESTAMP 
                                WHERE id = ?
                            """, (msg['id'],))
                        results.append({"id": msg['id'], "success": success == 0})
        
        return results

def create_digest(messages: List[sqlite3.Row], tier: TierType) -> str:
    """Create a digest message from multiple notifications"""
    count = len(messages)
    tier_emoji = {"critical": "🚨", "high": "📋", "medium": "ℹ️"}
    
    digest = f"{tier_emoji.get(tier, '📝')} **{tier.title()} Updates ({count} items)**\n\n"
    
    for i, msg in enumerate(messages, 1):
        digest += f"{i}. {msg['message']}\n"
    
    return digest

def main():
    """CLI interface for notification queue"""
    if len(sys.argv) < 2:
        print("Usage: notification-queue.py <command> [args...]")
        print("Commands:")
        print("  add <message> [--tier critical|high|medium] [--source source] [--bypass]")
        print("  flush <tier>")
        print("  status")
        return
    
    command = sys.argv[1]
    
    if command == "add":
        if len(sys.argv) < 3:
            print("Usage: notification-queue.py add <message> [options]")
            return
        
        message = sys.argv[2]
        tier = None
        source = ""
        bypass = False
        
        # Parse arguments
        i = 3
        while i < len(sys.argv):
            if sys.argv[i] == "--tier" and i + 1 < len(sys.argv):
                tier = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == "--source" and i + 1 < len(sys.argv):
                source = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == "--bypass":
                bypass = True
                i += 1
            else:
                i += 1
        
        message_id = add_to_queue(message, tier=tier, source=source, bypass=bypass)
        print(f"Added message {message_id} to queue")
    
    elif command == "flush":
        if len(sys.argv) < 3:
            print("Usage: notification-queue.py flush <tier>")
            return
        
        tier = sys.argv[2]
        results = flush_batch(tier)
        print(f"Flushed {len(results)} messages from {tier} tier")
    
    elif command == "status":
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT tier, status, COUNT(*) as count 
                FROM queue 
                GROUP BY tier, status
                ORDER BY tier, status
            """)
            
            print("Queue Status:")
            for row in cursor.fetchall():
                print(f"  {row[0]}/{row[1]}: {row[2]} messages")

if __name__ == "__main__":
    main()
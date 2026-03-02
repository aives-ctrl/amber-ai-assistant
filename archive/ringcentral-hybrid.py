#!/usr/bin/env python3
"""
RingCentral Hybrid Real-time - Fast polling (30 seconds) with instant notification
More reliable than WebSocket events for message detection
"""
import os
import sys
import json
import time
import subprocess
import asyncio
from datetime import datetime, timezone
from ringcentral import SDK

LAST_CHECK_FILE = '/Users/amberives/.openclaw/workspace/ringcentral-last-check-hybrid.txt'

class RingCentralHybrid:
    def __init__(self):
        self.running = False
        self.creds = self.load_credentials()
        
    def load_credentials(self):
        """Load RingCentral credentials"""
        env_path = '/Users/amberives/.openclaw/workspace/.env-ringcentral'
        creds = {}
        try:
            with open(env_path, 'r') as f:
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        creds[key] = value
            return creds
        except Exception as e:
            print(f"❌ Error loading credentials: {e}")
            return None
    
    def get_last_check_time(self):
        """Get timestamp of last check"""
        try:
            with open(LAST_CHECK_FILE, 'r') as f:
                return f.read().strip()
        except FileNotFoundError:
            # First run - use current time
            return datetime.now(timezone.utc).isoformat()
    
    def save_last_check_time(self):
        """Save current time as last check"""
        with open(LAST_CHECK_FILE, 'w') as f:
            f.write(datetime.now(timezone.utc).isoformat())
    
    def notify_message(self, text):
        """Send critical notification for new message"""
        try:
            display_text = text[:100]
            print(f"🔔 NEW RINGCENTRAL MESSAGE: {display_text}")
            
            # Send critical priority notification
            notify_cmd = [
                '/Users/amberives/.openclaw/workspace/scripts/notify',
                f'📱 RingCentral: "{display_text}"',
                '--tier', 'critical',
                '--source', 'ringcentral-hybrid'
            ]
            result = subprocess.run(notify_cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Notification sent: {result.stdout.strip()}")
            else:
                print(f"❌ Notification failed: {result.stderr.strip()}")
                
        except Exception as e:
            print(f"❌ Notification error: {e}")
    
    def check_new_messages(self):
        """Check for new messages since last check"""
        if not self.creds:
            return False
        
        last_check = self.get_last_check_time()
        
        try:
            # Authenticate
            sdk = SDK(self.creds['RINGCENTRAL_CLIENT_ID'], 
                     self.creds['RINGCENTRAL_CLIENT_SECRET'], 
                     self.creds['RINGCENTRAL_SERVER'])
            platform = sdk.platform()
            platform.login(jwt=self.creds['RINGCENTRAL_JWT'])
            
            # Get recent messages from direct chat
            chat_id = self.creds['RINGCENTRAL_DIRECT_CHAT_ID']
            response = platform.get(f'/restapi/v1.0/glip/chats/{chat_id}/posts', {'recordCount': 10})
            data = json.loads(response.text())
            
            new_messages = []
            for post in data.get('records', []):
                # Skip my own messages (I'm creator 3563197015)
                if post.get('creatorId') == '3563197015':
                    continue
                    
                # Check if message is newer than last check
                msg_time = post.get('creationTime', '')
                if msg_time > last_check:
                    text = post.get('text', '')
                    new_messages.append(text)
            
            # Process new messages
            for text in new_messages:
                self.notify_message(text)
            
            # Update last check time
            self.save_last_check_time()
            
            if new_messages:
                print(f"📱 Processed {len(new_messages)} new messages")
            
            return len(new_messages) > 0
            
        except Exception as e:
            print(f"❌ Check failed: {e}")
            return False
    
    async def run_fast_polling(self):
        """Run fast polling every 30 seconds"""
        self.running = True
        
        print("🚀 Starting RingCentral hybrid real-time (30-second polling)...")
        print("📱 Fast polling provides near-real-time notifications")
        
        while self.running:
            try:
                # Check for new messages
                found_new = self.check_new_messages()
                
                if found_new:
                    print(f"✅ Check completed - found new messages")
                else:
                    print(f"📭 Check completed - no new messages")
                
                # Wait 30 seconds before next check
                for i in range(30):
                    if not self.running:
                        break
                    await asyncio.sleep(1)
                    
            except Exception as e:
                print(f"❌ Polling error: {e}")
                await asyncio.sleep(30)
        
        print("👋 Fast polling stopped")
    
    def stop(self):
        """Stop the service"""
        self.running = False

async def main():
    """Main function"""
    hybrid = RingCentralHybrid()
    
    if not hybrid.creds:
        print("❌ Could not load credentials")
        sys.exit(1)
    
    import signal
    def signal_handler(sig, frame):
        print("\\n👋 Shutdown signal received...")
        hybrid.stop()
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        await hybrid.run_fast_polling()
    except KeyboardInterrupt:
        print("\\n👋 Interrupted")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\\n👋 Stopped")
    except Exception as e:
        print(f"❌ Failed to start: {e}")
        sys.exit(1)
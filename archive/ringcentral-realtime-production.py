#!/usr/bin/env python3
"""
RingCentral Real-time WebSocket Notifications - Production Version
Uses aiohttp for reliable WebSocket connections with proper error handling and reconnection
"""
import os
import sys
import json
import asyncio
import aiohttp
import subprocess
import signal
from datetime import datetime, timezone
from ringcentral import SDK

class RingCentralWebSocket:
    def __init__(self, creds):
        self.creds = creds
        self.session = None
        self.ws = None
        self.running = False
        self.reconnect_delay = 5
        self.max_reconnect_delay = 300  # 5 minutes
        self.subscription_id = None
        
    async def authenticate_and_get_token(self):
        """Authenticate with RingCentral and get WebSocket credentials"""
        sdk = SDK(self.creds['RINGCENTRAL_CLIENT_ID'], 
                 self.creds['RINGCENTRAL_CLIENT_SECRET'], 
                 self.creds['RINGCENTRAL_SERVER'])
        platform = sdk.platform()
        platform.login(jwt=self.creds['RINGCENTRAL_JWT'])
        
        ws = sdk.create_web_socket_client()
        token_response = ws.get_web_socket_token()
        
        return {
            'uri': token_response['uri'],
            'token': token_response['ws_access_token'],
            'expires_in': token_response['expires_in']
        }
    
    def notify_message(self, message_data):
        """Send notification when new message arrives"""
        try:
            sender = message_data.get('creatorId', 'Unknown')
            text = message_data.get('text', '')[:100]
            timestamp = message_data.get('creationTime', '')
            
            # Skip my own messages (I'm creator 3563197015)
            if sender == '3563197015':
                return
            
            print(f"🔔 NEW RINGCENTRAL MESSAGE!")
            print(f"   From: {sender}")
            print(f"   Time: {timestamp}")
            print(f"   Text: {text}")
            
            # Send critical priority notification for real-time messages
            notify_cmd = [
                '/Users/amberives/.openclaw/workspace/scripts/notify',
                f'📱 RingCentral: "{text}"',
                '--tier', 'critical',
                '--source', 'ringcentral-realtime'
            ]
            subprocess.run(notify_cmd, capture_output=True)
            
        except Exception as e:
            print(f"Error in message notification: {e}")
    
    async def handle_message(self, msg):
        """Handle incoming WebSocket messages"""
        try:
            if msg.type == aiohttp.WSMsgType.TEXT:
                data = json.loads(msg.data)
                
                # Handle different message types
                if isinstance(data, list):
                    for item in data:
                        await self.process_message(item)
                else:
                    await self.process_message(data)
                    
            elif msg.type == aiohttp.WSMsgType.ERROR:
                print(f"❌ WebSocket error: {self.ws.exception()}")
                
        except Exception as e:
            print(f"Error handling message: {e}")
    
    async def process_message(self, data):
        """Process individual WebSocket message"""
        try:
            msg_type = data.get('type')
            
            if msg_type == 'ConnectionDetails':
                print(f"✅ Connection established: {data.get('messageId', '')}")
                
            elif msg_type == 'ServerNotification':
                # This is the actual message notification
                body = data.get('body', {})
                event_type = data.get('event', '')
                
                if '/restapi/v1.0/glip/posts' in event_type:
                    # Check if it's our direct chat
                    group_id = body.get('groupId', '')
                    if group_id == self.creds['RINGCENTRAL_DIRECT_CHAT_ID']:
                        self.notify_message(body)
                        
            elif msg_type == 'ClientRequest':
                # Handle subscription responses
                if data.get('method') == 'POST' and '/subscription' in data.get('path', ''):
                    print(f"📋 Subscription response: {data}")
                    
        except Exception as e:
            print(f"Error processing message: {e}")
    
    async def create_subscription(self):
        """Create WebSocket subscription for message events"""
        subscription_request = {
            'type': 'ClientRequest',
            'messageId': f'sub-{int(datetime.now().timestamp())}',
            'method': 'POST',
            'path': '/restapi/v1.0/subscription',
            'body': {
                'eventFilters': ['/restapi/v1.0/glip/posts'],
                'deliveryMode': {
                    'transportType': 'WebSocket'
                }
            }
        }
        
        await self.ws.send_str(json.dumps(subscription_request))
        print("📤 Sent subscription request for message events")
    
    async def connect(self):
        """Establish WebSocket connection"""
        try:
            # Get fresh WebSocket credentials
            ws_creds = await self.authenticate_and_get_token()
            print(f"✅ Got WebSocket credentials (expires in {ws_creds['expires_in']}s)")
            
            # Create session if needed
            if not self.session:
                timeout = aiohttp.ClientTimeout(total=300, connect=30)
                self.session = aiohttp.ClientSession(timeout=timeout)
            
            # Connect to WebSocket
            headers = {
                'Authorization': f"Bearer {ws_creds['token']}",
                'User-Agent': 'OpenClaw-RingCentral/1.0'
            }
            
            self.ws = await self.session.ws_connect(
                ws_creds['uri'],
                headers=headers,
                heartbeat=30,
                compress=15
            )
            
            print("🔌 WebSocket connected successfully!")
            
            # Create subscription
            await self.create_subscription()
            
            # Reset reconnect delay on successful connection
            self.reconnect_delay = 5
            
            return True
            
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    async def disconnect(self):
        """Clean disconnect"""
        try:
            if self.ws:
                await self.ws.close()
            if self.session:
                await self.session.close()
        except:
            pass
    
    async def run_with_reconnection(self):
        """Main run loop with automatic reconnection"""
        self.running = True
        
        print("🚀 Starting RingCentral real-time notifications...")
        print("   Press Ctrl+C to stop")
        
        while self.running:
            try:
                # Attempt connection
                if await self.connect():
                    print("📱 REAL-TIME notifications active!")
                    
                    # Message processing loop
                    async for msg in self.ws:
                        if not self.running:
                            break
                        await self.handle_message(msg)
                        
                    print("⚠️ WebSocket connection closed")
                else:
                    print(f"❌ Connection failed, retrying in {self.reconnect_delay}s...")
                    await asyncio.sleep(self.reconnect_delay)
                    
                    # Exponential backoff
                    self.reconnect_delay = min(self.reconnect_delay * 2, self.max_reconnect_delay)
                    
            except asyncio.CancelledError:
                print("👋 Stopping RingCentral notifications...")
                break
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                print(f"⏰ Reconnecting in {self.reconnect_delay}s...")
                await asyncio.sleep(self.reconnect_delay)
        
        await self.disconnect()

def load_credentials():
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
        print(f"Error loading credentials: {e}")
        return None

async def main():
    """Main async function"""
    creds = load_credentials()
    if not creds:
        print("❌ Could not load credentials")
        sys.exit(1)
    
    # Create WebSocket client
    ws_client = RingCentralWebSocket(creds)
    
    # Handle shutdown signals
    def signal_handler(sig, frame):
        print("\\n👋 Shutdown signal received...")
        ws_client.running = False
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        await ws_client.run_with_reconnection()
    except KeyboardInterrupt:
        print("\\n👋 Stopping...")
    finally:
        await ws_client.disconnect()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\\n👋 Stopped")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)
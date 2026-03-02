#!/usr/bin/env python3
"""
RingCentral Real-time WebSocket - Final Working Version
Simplified but robust implementation for instant message notifications
"""
import os
import sys
import json
import asyncio
import aiohttp
import subprocess
import signal
from datetime import datetime
from ringcentral import SDK

class RingCentralRealTime:
    def __init__(self):
        self.running = False
        self.session = None
        self.ws = None
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
    
    def notify_message(self, text, sender_id):
        """Send critical notification for new message"""
        try:
            # Skip my own messages
            if sender_id == '3563197015':
                return
            
            display_text = text[:100]
            print(f"🔔 NEW MESSAGE: {display_text}")
            
            # Send critical priority notification
            notify_cmd = [
                '/Users/amberives/.openclaw/workspace/scripts/notify',
                f'📱 RingCentral: "{display_text}"',
                '--tier', 'critical',
                '--source', 'ringcentral-realtime'
            ]
            subprocess.run(notify_cmd, capture_output=True)
            
        except Exception as e:
            print(f"❌ Notification error: {e}")
    
    async def get_websocket_credentials(self):
        """Get WebSocket connection credentials"""
        try:
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
                'expires': token_response['expires_in']
            }
        except Exception as e:
            print(f"❌ Auth error: {e}")
            return None
    
    async def handle_websocket_message(self, msg_data):
        """Handle incoming WebSocket messages"""
        try:
            # Handle both list and single message formats
            messages = msg_data if isinstance(msg_data, list) else [msg_data]
            
            for msg in messages:
                msg_type = msg.get('type', '')
                
                if msg_type == 'ConnectionDetails':
                    print("✅ WebSocket connection established")
                    
                elif msg_type == 'ServerNotification':
                    # This is an actual message notification
                    body = msg.get('body', {})
                    event = msg.get('event', '')
                    
                    if '/restapi/v1.0/glip/posts' in event:
                        group_id = body.get('groupId', '')
                        # Check if it's our direct chat
                        if group_id == self.creds['RINGCENTRAL_DIRECT_CHAT_ID']:
                            text = body.get('text', '')
                            sender = body.get('creatorId', '')
                            self.notify_message(text, sender)
                
        except Exception as e:
            print(f"❌ Message handling error: {e}")
    
    async def run_realtime(self):
        """Main real-time WebSocket loop"""
        self.running = True
        
        print("🚀 Starting RingCentral real-time notifications...")
        
        while self.running:
            try:
                # Get fresh credentials
                ws_creds = await self.get_websocket_credentials()
                if not ws_creds:
                    print("❌ Could not get WebSocket credentials")
                    await asyncio.sleep(30)
                    continue
                
                print(f"✅ Got credentials (expires in {ws_creds['expires']}s)")
                
                # Create WebSocket session
                timeout = aiohttp.ClientTimeout(total=300, connect=30)
                self.session = aiohttp.ClientSession(timeout=timeout)
                
                headers = {
                    'Authorization': f"Bearer {ws_creds['token']}",
                    'User-Agent': 'OpenClaw-RingCentral/1.0'
                }
                
                # Connect and subscribe
                async with self.session.ws_connect(
                    ws_creds['uri'], 
                    headers=headers, 
                    heartbeat=30
                ) as self.ws:
                    
                    print("🔌 WebSocket connected!")
                    
                    # Create subscription for message events
                    subscription = {
                        'type': 'ClientRequest',
                        'messageId': f"sub-{int(datetime.now().timestamp())}",
                        'method': 'POST',
                        'path': '/restapi/v1.0/subscription',
                        'body': {
                            'eventFilters': ['/restapi/v1.0/glip/posts'],
                            'deliveryMode': {'transportType': 'WebSocket'}
                        }
                    }
                    
                    await self.ws.send_str(json.dumps(subscription))
                    print("📤 Subscription sent")
                    
                    print("📱 REAL-TIME NOTIFICATIONS ACTIVE!")
                    print("   Send me a RingCentral message to test...")
                    
                    # Message processing loop
                    async for msg in self.ws:
                        if not self.running:
                            break
                            
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            try:
                                data = json.loads(msg.data)
                                await self.handle_websocket_message(data)
                            except json.JSONDecodeError:
                                print(f"❌ Invalid JSON: {msg.data}")
                                
                        elif msg.type == aiohttp.WSMsgType.ERROR:
                            print(f"❌ WebSocket error: {self.ws.exception()}")
                            break
                
                await self.session.close()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"❌ Connection error: {e}")
                print("🔄 Reconnecting in 10 seconds...")
                await asyncio.sleep(10)
        
        print("👋 Real-time notifications stopped")
    
    def stop(self):
        """Stop the real-time service"""
        self.running = False

async def main():
    """Main function"""
    if not os.path.exists('/Users/amberives/.openclaw/workspace/.env-ringcentral'):
        print("❌ RingCentral credentials not found")
        sys.exit(1)
    
    realtime = RingCentralRealTime()
    
    if not realtime.creds:
        print("❌ Could not load credentials")
        sys.exit(1)
    
    # Handle shutdown signals
    def signal_handler(sig, frame):
        print("\\n👋 Shutdown signal received...")
        realtime.stop()
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        await realtime.run_realtime()
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
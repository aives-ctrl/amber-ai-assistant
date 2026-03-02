#!/usr/bin/env python3
"""
RingCentral Real-time WebSocket Notifications - Async Version
Instant push notifications when Dave sends messages using async/await
"""
import os
import sys
import json
import asyncio
import subprocess
from datetime import datetime
from ringcentral import SDK

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

def notify_message(message_data):
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
        
        # Send to notification queue for Dave
        notify_cmd = [
            '/Users/amberives/.openclaw/workspace/scripts/notify',
            f'📱 RingCentral: "{text}"',
            '--tier', 'critical',  # Use critical for instant real-time messages
            '--source', 'ringcentral-realtime'
        ]
        subprocess.run(notify_cmd, capture_output=True)
        
    except Exception as e:
        print(f"Error in message notification: {e}")

async def main():
    """Main async WebSocket subscription loop"""
    print("🚀 Starting RingCentral real-time notifications (async)...")
    
    creds = load_credentials()
    if not creds:
        print("❌ Could not load credentials")
        sys.exit(1)
    
    try:
        # Authenticate
        sdk = SDK(creds['RINGCENTRAL_CLIENT_ID'], creds['RINGCENTRAL_CLIENT_SECRET'], creds['RINGCENTRAL_SERVER'])
        platform = sdk.platform()
        platform.login(jwt=creds['RINGCENTRAL_JWT'])
        print("✅ Authenticated")
        
        # Create WebSocket client
        ws = sdk.create_web_socket_client()
        print("✅ WebSocket client created")
        
        # Get WebSocket credentials
        token_response = ws.get_web_socket_token()
        ws_uri = token_response['uri']
        ws_access_token = token_response['ws_access_token']
        expires_in = token_response['expires_in']
        
        print(f"✅ Got WebSocket credentials (expires in {expires_in}s)")
        
        # Set up event handlers
        def on_message(event):
            """Handle incoming message events"""
            try:
                event_data = json.loads(event) if isinstance(event, str) else event
                if event_data.get('event') == '/restapi/v1.0/glip/posts':
                    body = event_data.get('body', {})
                    # Check if it's our direct chat
                    if body.get('groupId') == creds['RINGCENTRAL_DIRECT_CHAT_ID']:
                        notify_message(body)
            except Exception as e:
                print(f"Error processing message event: {e}")
        
        def on_connect():
            print("✅ WebSocket connected - real-time notifications active!")
        
        def on_disconnect():
            print("⚠️ WebSocket disconnected - attempting reconnect...")
        
        def on_error(error):
            print(f"❌ WebSocket error: {error}")
        
        # Register event handlers
        ws.on('message', on_message)
        ws.on('connect', on_connect)
        ws.on('disconnect', on_disconnect)
        ws.on('error', on_error)
        
        # Open WebSocket connection (async)
        await ws.open_connection(ws_uri, ws_access_token)
        print("🔌 WebSocket connection opened")
        
        # Create subscription for message events (async)
        await ws.create_subscription([
            '/restapi/v1.0/glip/posts'  # Subscribe to all Glip message events
        ])
        print("✅ Subscribed to message events")
        
        print("📱 REAL-TIME RingCentral notifications active!")
        print("   Send me a message in RingCentral to test instantly...")
        print("   Press Ctrl+C to stop")
        
        # Keep alive loop (async)
        try:
            while True:
                await asyncio.sleep(30)  # Check every 30 seconds
                # Could add token refresh logic here if needed
        except KeyboardInterrupt:
            print("\\n👋 Stopping RingCentral real-time notifications...")
            await ws.close_connection()
            sys.exit(0)
            
    except Exception as e:
        print(f"❌ WebSocket setup failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    # Run the async main function
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\\n👋 Stopping...")
        sys.exit(0)
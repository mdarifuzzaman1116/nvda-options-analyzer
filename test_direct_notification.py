#!/usr/bin/env python3
"""
Direct notification test - sends a simple test message to ensure ntfy is working
"""

import requests
import time
from datetime import datetime

def send_test_notification():
    """Send a simple test notification to verify ntfy is working"""
    topic = "options_price"
    
    print("📱 Sending TEST notification to your phone...")
    print(f"📡 Topic: {topic}")
    print(f"⏰ Time: {datetime.now().strftime('%H:%M:%S')}")
    
    # Send a simple test message
    test_message = f"""🧪 TEST NOTIFICATION 🧪
⏰ Time: {datetime.now().strftime('%H:%M:%S')}
📱 This is a test to verify ntfy is working
🎯 If you see this, notifications are working!

Next step: Subscribe to this topic on your phone:
📲 Topic: options_price"""

    try:
        response = requests.post(
            f"https://ntfy.sh/{topic}",
            data=test_message.encode('utf-8'),
            headers={
                'Title': '🧪 NTFY TEST - Check Your Phone!',
                'Priority': 'urgent',
                'Tags': 'warning,bell,mobile_phone',
                'Content-Type': 'text/plain; charset=utf-8'
            },
            timeout=15
        )
        
        if response.status_code == 200:
            print("✅ Test notification sent successfully!")
            print(f"📱 Check your phone for notification from topic: {topic}")
            print(f"🌐 Or check: https://ntfy.sh/{topic}")
            return True
        else:
            print(f"❌ Failed to send notification. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error sending notification: {e}")
        return False

if __name__ == "__main__":
    print("🚀 DIRECT NTFY TEST")
    print("=" * 40)
    send_test_notification()
    print("=" * 40)
    print("📱 To receive notifications on your phone:")
    print("1. Download the ntfy app")
    print("2. Subscribe to topic: 'options_price'")
    print("3. Or use the web interface: https://ntfy.sh/options_price")

#!/usr/bin/env python3
"""
Test ntfy.sh notifications
"""

import sys
import os
import requests

# Add the current directory to Python path
sys.path.append('/Users/mdarifuzzaman/Documents/puts')

def test_ntfy():
    try:
        import config
        
        print("Testing ntfy.sh Configuration")
        print("=" * 40)
        
        # Check config
        notification_config = config.NOTIFICATION_CONFIG
        ntfy_config = notification_config.get('ntfy', {})
        
        if not ntfy_config.get('enabled'):
            print("ERROR: ntfy is not enabled in config")
            return
        
        topic = ntfy_config.get('topic')
        print(f"Topic: {topic}")
        
        if not topic:
            print("ERROR: No topic configured")
            return
        
        # Send test notification
        print("\nSending test notification...")
        
        url = f"https://ntfy.sh/{topic}"
        message = "Test from Options Analyzer!\n\nIf you see this, ntfy.sh is working perfectly!\n\nYour NVDA analysis will be sent here every hour."
        
        response = requests.post(
            url,
            data=message.encode('utf-8'),
            headers={
                'Title': 'Options Analyzer Test',
                'Priority': '3',
                'Tags': 'test,stocks',
                'Replace': 'test-notification'  # This will replace previous test notifications
            },
            timeout=10
        )
        
        if response.status_code == 200:
            print("SUCCESS: Test notification sent successfully!")
            print(f"Check your ntfy app for topic: {topic}")
            print()
            print("Next steps:")
            print("1. If you got the notification → Run: python sms_options_analyzer.py")
            print("2. If no notification → Install ntfy app and subscribe to topic")
        else:
            print(f"ERROR: Failed to send notification (HTTP {response.status_code})")
        
    except ImportError as e:
        print(f"ERROR: Import error: {e}")
        print("Make sure config.py exists")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_ntfy()

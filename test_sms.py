#!/usr/bin/env python3
"""
Test SMS functionality
Run this after you set up your Gmail App Password
"""

import sys
import os

# Add the current directory to Python path
sys.path.append('/Users/mdarifuzzaman/Documents/puts')

def test_sms():
    try:
        import config
        from sms_options_analyzer import AutomatedOptionsAnalyzer
        
        print("🧪 Testing SMS Configuration")
        print("=" * 40)
        
        # Check config
        notification_config = config.NOTIFICATION_CONFIG
        email_sms_config = notification_config.get('email_sms', {})
        
        if not email_sms_config.get('enabled'):
            print("❌ Email-to-SMS is not enabled in config")
            return
        
        print(f"📱 Phone: {email_sms_config['phone_number']}")
        print(f"📡 Carrier: {email_sms_config['carrier']}")
        print(f"📧 Email: {email_sms_config['from_email']}")
        
        # Check if app password is set
        if email_sms_config['app_password'] == 'your_gmail_app_password_here':
            print("❌ Gmail App Password not set!")
            print("Please update config.py with your real Gmail App Password")
            print("Get it from: https://myaccount.google.com/ > Security > App passwords")
            return
        
        print(f"🔑 App Password: {'*' * len(email_sms_config['app_password'])}")
        print()
        
        # Create test analyzer
        analyzer = AutomatedOptionsAnalyzer(
            ticker_symbol="TEST",
            price_range_below=30,
            notification_config=notification_config
        )
        
        # Send test SMS
        test_message = "🧪 SMS Test from Options Analyzer - Setup successful!"
        
        print("📤 Sending test SMS...")
        success = analyzer.send_email_sms(test_message)
        
        if success:
            print("✅ Test SMS sent successfully!")
            print("Check your phone for the test message")
        else:
            print("❌ Failed to send SMS")
            print("Check the logs for more details")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure config.py exists and is properly formatted")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_sms()

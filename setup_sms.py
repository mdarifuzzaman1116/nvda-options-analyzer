#!/usr/bin/env python3
"""
Setup script for SMS/Text Notifications - Automated Options Analyzer
This script helps you configure FREE text message notifications
"""

import os
import sys
import requests

def test_ntfy(topic):
    """Test ntfy.sh notification (completely free)"""
    try:
        url = f"https://ntfy.sh/{topic}"
        response = requests.post(
            url,
            data="🧪 Test message from Options Analyzer setup",
            headers={'Title': 'Setup Test'},
            timeout=10
        )
        return response.status_code == 200
    except:
        return False

def create_sms_config():
    """Interactive setup for SMS/text notifications"""
    print("📱 SMS/Text Notification Setup")
    print("=" * 50)
    print("Choose your preferred FREE notification method(s):")
    print()
    print("1. 📧 Email-to-SMS (via your phone carrier)")
    print("   ✅ Completely free")
    print("   ✅ Works with all major carriers")
    print("   ⚠️  Requires Gmail account")
    print()
    print("2. 🔔 ntfy.sh (push notifications)")
    print("   ✅ Completely free, no signup")
    print("   ✅ Works on phone/desktop")
    print("   ✅ Install ntfy app from app store")
    print()
    print("3. 💬 Discord Webhook")
    print("   ✅ Free Discord account needed")
    print("   ✅ Get notifications in Discord")
    print()
    print("4. 📲 Pushover (premium option)")
    print("   💰 $5 one-time fee after free trial")
    print("   ✅ Very reliable notifications")
    print()
    
    methods = input("Enter methods to configure (1,2,3,4): ").strip().split(',')
    
    config = {}
    
    # Email-to-SMS setup
    if '1' in methods:
        print("\n📧 Email-to-SMS Setup")
        print("-" * 30)
        print("This sends SMS via your phone carrier's email gateway")
        print("You'll need the same Gmail setup as before.")
        print()
        
        phone = input("Enter your phone number (10 digits, no spaces): ").strip().replace('-', '').replace('(', '').replace(')', '').replace(' ', '')
        print("\nSupported carriers:")
        print("• verizon")
        print("• att (or at&t)")
        print("• tmobile (or t-mobile)")
        print("• sprint")
        print("• boost (or boost mobile)")
        print("• cricket (or cricket wireless)")
        print("• uscellular (or us cellular)")
        print("• metro (or metropcs)")
        print("• mint (or mint mobile)")
        carrier = input("Enter your carrier: ").strip().lower()
        
        gmail = input("Enter your Gmail address: ").strip()
        print("\n🔑 You'll need the same Gmail App Password from before")
        print("If you don't have one, see: https://support.google.com/accounts/answer/185833")
        app_password = input("Enter Gmail app password: ").strip()
        
        config['email_sms'] = {
            'enabled': True,
            'phone_number': phone,
            'carrier': carrier,
            'from_email': gmail,
            'app_password': app_password
        }
        
        print("✅ Email-to-SMS configured")
    
    # ntfy.sh setup  
    if '2' in methods:
        print("\n🔔 ntfy.sh Setup")
        print("-" * 20)
        print("ntfy.sh is completely free and doesn't require signup!")
        print("1. Install 'ntfy' app from your phone's app store")
        print("2. Choose a unique topic name (like 'john_options_2024')")
        print("3. Subscribe to that topic in the app")
        print()
        
        topic = input("Enter your unique topic name: ").strip()
        
        print(f"\n🧪 Testing ntfy notification to topic '{topic}'...")
        if test_ntfy(topic):
            print("✅ Test notification sent!")
            print(f"Check your ntfy app for the test message")
            confirm = input("Did you receive the test notification? (y/n): ").lower()
            if confirm == 'y':
                config['ntfy'] = {
                    'enabled': True,
                    'topic': topic
                }
                print("✅ ntfy.sh configured successfully")
            else:
                print("⚠️  ntfy.sh test failed, but configuration saved anyway")
                config['ntfy'] = {
                    'enabled': True,
                    'topic': topic
                }
        else:
            print("❌ ntfy test failed")
    
    # Discord Webhook setup
    if '3' in methods:
        print("\n💬 Discord Webhook Setup")
        print("-" * 25)
        print("To set up Discord webhook:")
        print("1. Create a Discord server (or use existing)")
        print("2. Go to Server Settings > Integrations > Webhooks")
        print("3. Create New Webhook, copy the URL")
        print()
        
        webhook_url = input("Enter Discord webhook URL: ").strip()
        
        config['webhook'] = {
            'enabled': True,
            'type': 'discord',
            'url': webhook_url
        }
        
        print("✅ Discord webhook configured")
    
    # Pushover setup
    if '4' in methods:
        print("\n📲 Pushover Setup")
        print("-" * 17)
        print("Pushover requires:")
        print("1. Pushover account (pushover.net)")
        print("2. App token and user key")
        print("3. $5 one-time fee after 7-day trial")
        print()
        
        app_token = input("Enter Pushover app token: ").strip()
        user_key = input("Enter Pushover user key: ").strip()
        
        config['pushover'] = {
            'enabled': True,
            'app_token': app_token,
            'user_key': user_key
        }
        
        print("✅ Pushover configured")
    
    return config

def main():
    """Main setup function"""
    print("📱 FREE SMS/Text Notification Setup")
    print("Send options analysis alerts to your phone!")
    print()
    
    # Check if config already exists
    config_path = '/Users/mdarifuzzaman/Documents/puts/config.py'
    if os.path.exists(config_path):
        overwrite = input("Config file exists. Add SMS notifications? (y/n): ").lower()
        if overwrite != 'y':
            print("Setup cancelled.")
            return
    
    # Get analysis preferences
    print("📊 Analysis Configuration")
    ticker = input("Enter stock ticker to analyze [NVDA]: ").strip().upper() or "NVDA"
    
    try:
        price_range = float(input("Enter price range below current price [40]: ") or "40")
    except ValueError:
        price_range = 40
    
    print("\n⏰ Schedule Configuration")
    print("Options: hour, 30minutes, 2hours, day")
    schedule_interval = input("How often to run analysis [hour]: ").strip() or "hour"
    
    # Setup notifications
    notification_config = create_sms_config()
    
    # Create config.py file
    config_content = f'''# SMS Options Analyzer Configuration
# Generated by setup script

NOTIFICATION_CONFIG = {repr(notification_config)}

ANALYSIS_CONFIG = {{
    'ticker': '{ticker}',
    'price_range': {price_range},
    'schedule_interval': '{schedule_interval}'
}}

NOTIFICATION_SETTINGS = {{
    'send_notifications': True,
    'notification_type': 'sms'  # 'sms' or 'email'
}}

LOG_CONFIG = {{
    'log_file': '/Users/mdarifuzzaman/Documents/puts/options_analyzer.log',
    'log_level': 'INFO'
}}
'''
    
    # Write config file
    with open(config_path, 'w') as f:
        f.write(config_content)
    
    print(f"\n✅ Configuration saved to {config_path}")
    
    # Send test notifications
    if notification_config:
        test_send = input("\n📱 Send test notifications now? (y/n): ").lower()
        if test_send == 'y':
            print("🧪 Sending test notifications...")
            
            # Import and test
            sys.path.append('/Users/mdarifuzzaman/Documents/puts')
            from sms_options_analyzer import AutomatedOptionsAnalyzer
            
            # Create test message
            test_analyzer = AutomatedOptionsAnalyzer(
                ticker_symbol=ticker,
                price_range_below=price_range,
                notification_config=notification_config
            )
            
            # Send test SMS
            test_message = f"🧪 Options Analyzer Test - {ticker} analysis will be sent to this number every {schedule_interval}!"
            
            success_count = 0
            if notification_config.get('email_sms', {}).get('enabled'):
                if test_analyzer.send_email_sms(test_message):
                    success_count += 1
                    print("✅ SMS test sent!")
            
            if notification_config.get('ntfy', {}).get('enabled'):
                if test_analyzer.send_ntfy_notification(test_message):
                    success_count += 1
                    print("✅ ntfy test sent!")
            
            if notification_config.get('webhook', {}).get('enabled'):
                if test_analyzer.send_webhook_notification(test_message):
                    success_count += 1
                    print("✅ Webhook test sent!")
            
            if notification_config.get('pushover', {}).get('enabled'):
                if test_analyzer.send_pushover_notification(test_message):
                    success_count += 1
                    print("✅ Pushover test sent!")
            
            if success_count > 0:
                print(f"🎉 {success_count} notification method(s) working!")
            else:
                print("⚠️  No notifications sent successfully")
    
    print("\n🎉 Setup complete!")
    print("\nNext steps:")
    print("1. Run: python sms_options_analyzer.py")
    print("2. The analyzer will text you results every hour")
    print("3. Check the log file for detailed information")
    print("4. Press Ctrl+C to stop the analyzer")
    print()
    
    # Ask if they want to start now
    start_now = input("Start the SMS analyzer now? (y/n): ").lower()
    if start_now == 'y':
        os.system('python /Users/mdarifuzzaman/Documents/puts/sms_options_analyzer.py')

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
SMS Launcher for the Automated Options Analyzer
Free text message notifications for your options analysis!
"""

import os
import sys

def main():
    script_dir = '/Users/mdarifuzzaman/Documents/puts'
    
    print("📱 SMS Options Analyzer Launcher")
    print("=" * 45)
    print("1. 🆕 Setup SMS notifications (FREE)")
    print("2. 🚀 Start SMS analyzer")
    print("3. 📊 Run single analysis with SMS")
    print("4. 📋 View logs")
    print("5. 🧪 Test notifications only")
    print("6. 📧 Switch to email version")
    print("7. ❌ Exit")
    print()
    
    choice = input("Select option (1-7): ").strip()
    
    if choice == "1":
        print("\n🔧 Setting up FREE SMS notifications...")
        print("Available options:")
        print("• 📧 Email-to-SMS (via phone carrier) - FREE")
        print("• 🔔 ntfy.sh push notifications - FREE") 
        print("• 💬 Discord webhooks - FREE")
        print("• 📲 Pushover - $5 one-time fee")
        print()
        os.system(f'cd {script_dir} && python setup_sms.py')
    
    elif choice == "2":
        if not os.path.exists(f'{script_dir}/config.py'):
            print("❌ Configuration not found. Please run setup first (option 1)")
            return
        print("\n🚀 Starting SMS analyzer...")
        print("You'll receive text messages with analysis results!")
        print("Press Ctrl+C to stop")
        os.system(f'cd {script_dir} && python sms_options_analyzer.py')
    
    elif choice == "3":
        if not os.path.exists(f'{script_dir}/config.py'):
            print("❌ Configuration not found. Please run setup first (option 1)")
            return
        print("\n📊 Running single analysis with SMS...")
        # Import config and run once
        sys.path.append(script_dir)
        try:
            import config
            from sms_options_analyzer import AutomatedOptionsAnalyzer
            
            analyzer = AutomatedOptionsAnalyzer(
                ticker_symbol=config.ANALYSIS_CONFIG['ticker'],
                price_range_below=config.ANALYSIS_CONFIG['price_range'],
                notification_config=config.NOTIFICATION_CONFIG
            )
            analyzer.run_automated_analysis()
            print("✅ Analysis completed and SMS sent!")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    elif choice == "4":
        log_file = f'{script_dir}/options_analyzer.log'
        if os.path.exists(log_file):
            print("\n📋 Last 20 log entries:")
            os.system(f'tail -20 {log_file}')
        else:
            print("❌ No log file found")
    
    elif choice == "5":
        if not os.path.exists(f'{script_dir}/config.py'):
            print("❌ Configuration not found. Please run setup first (option 1)")
            return
        print("\n🧪 Testing notifications...")
        sys.path.append(script_dir)
        try:
            import config
            from sms_options_analyzer import AutomatedOptionsAnalyzer
            
            analyzer = AutomatedOptionsAnalyzer(
                ticker_symbol="TEST",
                price_range_below=30,
                notification_config=config.NOTIFICATION_CONFIG
            )
            
            test_message = "🧪 This is a test message from your Options Analyzer!"
            
            success = False
            if config.NOTIFICATION_CONFIG.get('email_sms', {}).get('enabled'):
                if analyzer.send_email_sms(test_message):
                    print("✅ SMS test sent!")
                    success = True
            
            if config.NOTIFICATION_CONFIG.get('ntfy', {}).get('enabled'):
                if analyzer.send_ntfy_notification(test_message):
                    print("✅ ntfy test sent!")
                    success = True
            
            if config.NOTIFICATION_CONFIG.get('webhook', {}).get('enabled'):
                if analyzer.send_webhook_notification(test_message):
                    print("✅ Webhook test sent!")
                    success = True
            
            if config.NOTIFICATION_CONFIG.get('pushover', {}).get('enabled'):
                if analyzer.send_pushover_notification(test_message):
                    print("✅ Pushover test sent!")
                    success = True
            
            if not success:
                print("❌ No notifications configured or all failed")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    elif choice == "6":
        print("\n📧 Switching to email version...")
        if os.path.exists(f'{script_dir}/launch.py'):
            os.system(f'cd {script_dir} && python launch.py')
        else:
            print("❌ Email launcher not found")
    
    elif choice == "7":
        print("👋 Goodbye!")
        return
    
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Quick launcher for the Automated Options Analyzer
Run this script to start the automated system
"""

import os
import sys

def main():
    script_dir = '/Users/mdarifuzzaman/Documents/puts'
    
    print("🎯 Options Analyzer Launcher")
    print("=" * 40)
    print("1. First-time setup")
    print("2. Start automated analyzer")
    print("3. Run single analysis")
    print("4. View logs")
    print("5. Exit")
    print()
    
    choice = input("Select option (1-5): ").strip()
    
    if choice == "1":
        print("\n🔧 Running first-time setup...")
        os.system(f'cd {script_dir} && python setup_automation.py')
    
    elif choice == "2":
        if not os.path.exists(f'{script_dir}/config.py'):
            print("❌ Configuration not found. Please run setup first (option 1)")
            return
        print("\n🚀 Starting automated analyzer...")
        print("Press Ctrl+C to stop")
        os.system(f'cd {script_dir} && python automated_options_analyzer.py')
    
    elif choice == "3":
        if not os.path.exists(f'{script_dir}/config.py'):
            print("❌ Configuration not found. Please run setup first (option 1)")
            return
        print("\n📊 Running single analysis...")
        # Import config and run once
        sys.path.append(script_dir)
        try:
            import config
            from automated_options_analyzer import AutomatedOptionsAnalyzer
            
            analyzer = AutomatedOptionsAnalyzer(
                ticker_symbol=config.ANALYSIS_CONFIG['ticker'],
                price_range_below=config.ANALYSIS_CONFIG['price_range'],
                email_config=config.EMAIL_CONFIG
            )
            analyzer.run_automated_analysis()
            print("✅ Analysis completed!")
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
        print("👋 Goodbye!")
        return
    
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()

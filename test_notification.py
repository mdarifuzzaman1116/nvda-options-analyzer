#!/usr/bin/env python3
"""
Test script to run AAPL options analysis and send notification to ntfy
"""

import sys
import os
import logging
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from comprehensive_analyzer import ComprehensiveOptionsAnalyzer
from config import NOTIFICATION_CONFIG

def test_notification():
    """Run a quick test of the notification system"""
    print("🚀 Starting AAPL Options Analysis Test...")
    print(f"⏰ Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("📱 Will send notification to ntfy.sh/options_price")
    print("=" * 50)
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    try:
        # Run the analyzer
        analyzer = ComprehensiveOptionsAnalyzer()
        print("📊 Analyzing AAPL options...")
        results = analyzer.analyze_all_stocks()
        
        if not results:
            print("❌ No results returned from analyzer")
            return
        
        # Generate the report
        print("📝 Generating comprehensive report...")
        report = analyzer.create_comprehensive_report(results)
        
        if not report:
            print("❌ No report generated")
            return
        
        print("✅ Report generated successfully!")
        print(f"📏 Report length: {len(report)} characters")
        print("\n" + "=" * 50)
        print("📄 REPORT PREVIEW (first 500 chars):")
        print("=" * 50)
        print(report[:500] + "..." if len(report) > 500 else report)
        print("=" * 50)
        
        # Send notification
        print("\n📱 Sending notification to ntfy...")
        
        # Import the notification function
        from efficient_analyzer import send_single_stock_notification
        
        topic = NOTIFICATION_CONFIG['ntfy']['topic']
        print(f"📡 Sending to topic: {topic}")
        
        success = send_single_stock_notification(report['AAPL'], 'AAPL', topic)
        
        if success:
            print("✅ Notification sent successfully!")
            print(f"📱 Check your phone or visit: https://ntfy.sh/{topic}")
        else:
            print("❌ Failed to send notification")
        
    except Exception as e:
        print(f"❌ Error during test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_notification()

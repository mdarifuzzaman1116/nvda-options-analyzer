#!/usr/bin/env python3
"""
Quick test to verify dynamic week detection works for all stocks
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from comprehensive_analyzer import ComprehensiveOptionsAnalyzer
from efficient_analyzer import send_single_stock_notification

def test_all_stocks():
    """Test table format for all stocks to ensure dynamic week detection works"""
    print("🧪 Testing dynamic table format for all stocks...")
    
    # Get data for all stocks
    analyzer = ComprehensiveOptionsAnalyzer()
    results = analyzer.analyze_all_stocks()
    
    if results:
        stock_reports = analyzer.create_comprehensive_report(results)
        
        # Test each stock individually (without the 3-minute delays)
        for symbol in ['AAPL', 'NVDA', 'GOOG', 'GOOGL']:
            if symbol in stock_reports:
                print(f"\n{'='*60}")
                print(f"🔍 Testing {symbol} Table Format")
                print('='*60)
                
                # Test the notification format
                success = send_single_stock_notification(
                    stock_reports[symbol], 
                    symbol, 
                    'test_topic'  # Use test topic, won't actually send
                )
                
                if success:
                    print(f"✅ {symbol} table format: SUCCESS")
                else:
                    print(f"❌ {symbol} table format: FAILED")
            else:
                print(f"⚠️ {symbol}: No data available")
    
    print(f"\n{'='*60}")
    print("🎯 Dynamic table format test completed!")
    print('='*60)

if __name__ == "__main__":
    test_all_stocks()

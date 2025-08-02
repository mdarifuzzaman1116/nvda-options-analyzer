#!/usr/bin/env python3
"""
Instant AAPL Options Analysis
Shows results immediately without background processes
"""

import sys
import os
import time

# Add current directory to path  
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def run_instant_analysis():
    """Run analysis and show results immediately"""
    print("🚀 INSTANT ANALYSIS: AAPL Options")
    print("⏰ Running live analysis...")
    
    try:
        from comprehensive_analyzer import ComprehensiveOptionsAnalyzer
        
        # Create analyzer
        start_time = time.time()
        analyzer = ComprehensiveOptionsAnalyzer()
        
        print("📊 Fetching AAPL options data...")
        
        # Run analysis
        results = analyzer.analyze_all_stocks()
        
        if results:
            # Generate report
            report = analyzer.create_comprehensive_report(results)
            
            duration = time.time() - start_time
            
            print(f"✅ Analysis completed in {duration:.1f} seconds")
            print("=" * 60)
            print("📊 AAPL OPTIONS ANALYSIS RESULTS:")
            print("=" * 60)
            print(report)
            print("=" * 60)
            print(f"🎯 Found {len(results)} analysis results")
            print("💰 All premiums are per share (×100 for contract value)")
            
            return True
        else:
            print("❌ No analysis results obtained")
            return False
            
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        return False

if __name__ == "__main__":
    run_instant_analysis()

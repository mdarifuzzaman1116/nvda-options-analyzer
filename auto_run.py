#!/usr/bin/env python3
"""
Auto-run script for AAPL options analysis
Runs automatically without user interaction
"""

import sys
import time
import logging
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from efficient_analyzer import run_analysis_with_timeout, setup_logging

def main():
    """Run analysis automatically"""
    print("🚀 AUTO-RUN: Starting AAPL options analysis...")
    print("⏰ This will complete automatically in ~3-5 seconds")
    print("=" * 50)
    
    # Setup logging
    logger = setup_logging()
    
    # Record start time
    start_time = time.time()
    
    try:
        # Run the analysis
        run_analysis_with_timeout()
        
        # Calculate duration
        end_time = time.time()
        duration = end_time - start_time
        
        print("=" * 50)
        print(f"✅ AUTO-RUN COMPLETED in {duration:.1f} seconds")
        print("📱 Check your ntfy app for AAPL options notifications!")
        print("💰 Analysis covered 4 weeks of AAPL put options")
        print("🎯 Notifications sent with color-coded buy signals")
        
        return True
        
    except Exception as e:
        print("=" * 50)
        print(f"❌ AUTO-RUN FAILED: {e}")
        return False

if __name__ == "__main__":
    main()

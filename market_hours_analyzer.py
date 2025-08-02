#!/usr/bin/env python3
"""
Market Hours Options Analyzer
Runs only during stock market hours (9 AM - 4 PM EST, Monday-Friday)
Optimized for GitHub Codespaces free tier (60 hours/month)
"""

import os
import sys
import time
import logging
import schedule
from datetime import datetime, timezone
import pytz

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our analyzer
from sms_options_analyzer import AutomatedOptionsAnalyzer

def setup_logging():
    """Setup logging for market hours analyzer"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('market_hours_analyzer.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

def is_market_hours():
    """Check if current time is during market hours (9 AM - 4 PM EST, Monday-Friday)"""
    # Define EST timezone
    est = pytz.timezone('US/Eastern')
    now = datetime.now(est)
    
    # Check if it's a weekday (Monday=0, Sunday=6)
    if now.weekday() >= 5:  # Saturday or Sunday
        return False
    
    # Check if it's between 9 AM and 4 PM EST
    market_open = now.replace(hour=9, minute=0, second=0, microsecond=0)
    market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)
    
    return market_open <= now <= market_close

def run_analysis():
    """Run NVDA analysis and send notification"""
    logger = logging.getLogger(__name__)
    
    if not is_market_hours():
        logger.info("⏰ Outside market hours - skipping analysis")
        return
    
    try:
        logger.info("🚀 Starting hourly NVDA analysis...")
        analyzer = AutomatedOptionsAnalyzer()
        
        # Run single analysis (not continuous)
        success = analyzer.run_single_analysis()
        
        if success:
            logger.info("✅ Analysis completed successfully")
        else:
            logger.error("❌ Analysis failed")
            
    except Exception as e:
        logger.error(f"💥 Error during analysis: {e}")

def wait_for_market_hours():
    """Wait until market hours if currently outside"""
    logger = logging.getLogger(__name__)
    est = pytz.timezone('US/Eastern')
    
    while True:
        now = datetime.now(est)
        
        # If it's weekend, wait until Monday 9 AM
        if now.weekday() >= 5:  # Weekend
            days_until_monday = (7 - now.weekday()) % 7
            if days_until_monday == 0:  # It's Sunday
                days_until_monday = 1
            
            next_monday_9am = now.replace(hour=9, minute=0, second=0, microsecond=0) + \
                            datetime.timedelta(days=days_until_monday)
            
            logger.info(f"📅 Weekend detected. Next market open: {next_monday_9am.strftime('%A %Y-%m-%d %H:%M %Z')}")
            break
        
        # If it's before 9 AM on weekday
        if now.hour < 9:
            next_open = now.replace(hour=9, minute=0, second=0, microsecond=0)
            logger.info(f"🌅 Before market hours. Market opens at: {next_open.strftime('%H:%M %Z')}")
            break
        
        # If it's after 4 PM on weekday
        if now.hour >= 16:
            if now.weekday() == 4:  # Friday
                # Next market day is Monday
                next_monday_9am = now.replace(hour=9, minute=0, second=0, microsecond=0) + \
                                datetime.timedelta(days=3)
                logger.info(f"🏁 After Friday market close. Next market open: {next_monday_9am.strftime('%A %Y-%m-%d %H:%M %Z')}")
            else:
                # Next market day is tomorrow
                tomorrow_9am = now.replace(hour=9, minute=0, second=0, microsecond=0) + \
                             datetime.timedelta(days=1)
                logger.info(f"🌙 After market hours. Next market open: {tomorrow_9am.strftime('%A %Y-%m-%d %H:%M %Z')}")
            break
        
        # We're in market hours
        logger.info("📈 Currently in market hours")
        return

def main():
    """Main function for market hours analyzer"""
    logger = setup_logging()
    logger.info("🏦 Starting Market Hours NVDA Options Analyzer")
    logger.info("📅 Schedule: Monday-Friday, 9 AM - 4 PM EST")
    logger.info("⏰ Frequency: Every hour during market hours")
    logger.info("💰 Optimized for GitHub Codespaces (60 hours/month free)")
    
    # Check if config exists
    try:
        import config
        logger.info("✅ Configuration loaded successfully")
    except ImportError:
        logger.error("❌ Configuration not found!")
        logger.info("📝 Creating default configuration...")
        
        # Create default config for market hours
        config_content = '''
# Configuration for Market Hours Options Analyzer
ANALYSIS_CONFIG = {
    'ticker': 'NVDA',
    'price_range_below': 30,
    'enabled': True
}

NOTIFICATION_CONFIG = {
    'ntfy': {
        'enabled': True,
        'topic': 'options_price'
    }
}
'''
        with open('config.py', 'w') as f:
            f.write(config_content)
        logger.info("✅ Default configuration created")
    
    # Wait for market hours if needed
    wait_for_market_hours()
    
    # Schedule analysis every hour during market hours
    schedule.every().hour.do(run_analysis)
    
    logger.info("🔄 Scheduler started - will run every hour during market hours")
    
    try:
        while True:
            # Check if we're still in market hours
            if not is_market_hours():
                logger.info("⏰ Market closed - stopping scheduler")
                break
            
            # Run pending scheduled jobs
            schedule.run_pending()
            
            # Sleep for 1 minute before checking again
            time.sleep(60)
            
        logger.info("🛑 Scheduler stopped - outside market hours")
        
    except KeyboardInterrupt:
        logger.info("👋 Analyzer stopped by user")
    except Exception as e:
        logger.error(f"💥 Error: {e}")

if __name__ == "__main__":
    main()

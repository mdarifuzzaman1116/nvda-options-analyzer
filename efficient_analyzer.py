#!/usr/bin/env python3
"""
Efficient Market Hours Options Analyzer
Runs for 2 minutes every hour then stops to save resources
Optimized for GitHub Codespaces free tier: 14 minutes/day instead of 7 hours/day
"""

import os
import sys
import time
import logging
import schedule
import threading
import requests
from datetime import datetime, timezone
import pytz

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our analyzers
from comprehensive_analyzer import ComprehensiveOptionsAnalyzer

# Testing mode flag - GitHub Actions will always run regardless of day/time
TESTING_MODE = True  # GitHub Actions handles scheduling, so always run when triggered

def setup_logging():
    """Setup logging for efficient analyzer"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('efficient_analyzer.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

def send_multi_stock_notifications(stock_reports, topic):
    """Send separate notifications for each stock, 3 minutes apart"""
    try:
        import requests
        import time
        
        stock_order = ['AAPL', 'NVDA', 'GOOG', 'GOOGL']  # Order for notifications
        successful_sends = 0
        
        for i, symbol in enumerate(stock_order):
            if symbol not in stock_reports:
                logging.info(f"⏭️ Skipping {symbol} - no data available")
                continue
                
            report = stock_reports[symbol]
            
            # Add delay between stocks (except for first one) - Resource Conservation
            if i > 0:
                delay_minutes = 3  # 3-minute pause to conserve resources
                logging.info(f"⏱️ Waiting {delay_minutes} minutes before sending {symbol} notification...")
                logging.info(f"💤 Resource conservation: Pausing for {delay_minutes} min between stocks")
                time.sleep(delay_minutes * 60)  # 3 minutes = 180 seconds
            
            logging.info(f"📤 Sending {symbol} notification...")
            
            success = send_single_stock_notification(report, symbol, topic)
            if success:
                successful_sends += 1
                logging.info(f"✅ {symbol} notification sent successfully!")
            else:
                logging.error(f"❌ Failed to send {symbol} notification")
        
        return successful_sends > 0
        
    except Exception as e:
        logging.error(f"Failed to send multi-stock notifications: {e}")
        return False

def send_single_stock_notification(report, symbol, topic):
    """Send optimized notification with ALL 4 WEEKS and TOP 10 STRIKES visible"""
    try:
        import requests
        
        # PREVIEW what we're about to send
        print(f"\n" + "="*80)
        print(f"📱 SENDING {symbol} NOTIFICATION PREVIEW")
        print("="*80)
        
        # Extract ABSOLUTE BEST CHOICE
        absolute_best = ""
        if "⭐ === ABSOLUTE BEST CHOICE === ⭐" in report:
            start = report.find("⭐ === ABSOLUTE BEST CHOICE === ⭐")
            end = report.find("========================================", start)
            if end != -1:
                absolute_best = report[start:end].strip()
        
        # Extract WEEKLY SUMMARY (only once)
        weekly_summary = ""
        if "🏆 === WEEKLY BEST PICKS SUMMARY === 🏆" in report:
            start = report.find("🏆 === WEEKLY BEST PICKS SUMMARY === 🏆")
            end = report.find("============================================================", start)
            if end != -1:
                weekly_summary = report[start:end].strip()
        
        # Create condensed ALL 4 WEEKS detailed analysis
        condensed_weeks = f"📊 === ALL 4 WEEKS TOP 10 STRIKES === 📊\n"
        
        # Extract key info for each week
        weeks_data = [
            ("WEEK 1 - 2025-08-08", "Days: 5"),
            ("WEEK 2 - 2025-08-15", "Days: 12"), 
            ("WEEK 3 - 2025-08-22", "Days: 19"),
            ("WEEK 4 - 2025-08-29", "Days: 26")
        ]
        
        for week_name, days_info in weeks_data:
            if week_name in report:
                week_start = report.find(week_name)
                # Find next week or end
                next_week_pos = len(report)
                for next_week, _ in weeks_data:
                    if next_week != week_name:
                        pos = report.find(next_week, week_start + 1)
                        if pos != -1 and pos < next_week_pos:
                            next_week_pos = pos
                
                week_section = report[week_start:next_week_pos]
                
                # Extract top 10 strikes with key info
                condensed_weeks += f"📅 {week_name}\n"
                
                strike_count = 0
                lines = week_section.split('\n')
                current_strike = None
                current_premium = None
                current_risk = None
                
                for line in lines:
                    if "Strike" in line and "$" in line and strike_count < 10:  # Show top 10
                        # Extract strike price
                        strike_start = line.find("$")
                        strike_end = line.find(" ", strike_start)
                        if strike_end == -1:
                            strike_end = len(line)
                        current_strike = line[strike_start:strike_end]
                    elif "Premium: $" in line and current_strike:
                        prem_start = line.find("$") + 1
                        prem_end = line.find(" ", prem_start)
                        if prem_end == -1:
                            prem_end = len(line)
                        current_premium = "$" + line[prem_start:prem_end]
                    elif "Risk: " in line and current_strike and current_premium:
                        risk_start = line.find("Risk: ") + 6
                        risk_end = line.find("%", risk_start) + 1
                        if risk_end > 6:
                            current_risk = line[risk_start:risk_end]
                            
                            strike_count += 1
                            # Use compact format for 10 strikes
                            condensed_weeks += f"  #{strike_count:2d} {current_strike} • {current_premium} • {current_risk}\n"
                            
                            # Reset for next strike
                            current_strike = None
                            current_premium = None
                            current_risk = None
                
                condensed_weeks += "\n"
        
        # Build final clean notification (no duplicates)
        final_report = ""
        
        if absolute_best:
            final_report += f"🚨 URGENT {symbol} ALERT 🚨\n" + absolute_best + "\n\n"
        
        # Skip weekly summary to save space for 10 strikes per week
        # if weekly_summary:
        #     final_report += weekly_summary + "\n\n"
        
        # Add detailed ALL 4 WEEKS analysis (10 strikes each)
        final_report += condensed_weeks
        
        # Ensure it fits in one notification - be more aggressive with trimming
        if len(final_report) > 3900:
            final_report = final_report[:3800]
            last_newline = final_report.rfind('\n')
            if last_newline > 3600:
                final_report = final_report[:last_newline]
            final_report += "\n\n📱 More strikes in app"
        
        # PREVIEW in terminal
        print(f"Length: {len(final_report)} characters")
        print("-"*80)
        print(final_report)
        print("="*80)
        
        # Send notification
        url = f"https://ntfy.sh/{topic}"
        headers = {
            'Title': f'{symbol} TOP 10 STRIKES/WEEK',
            'Priority': 'urgent',
            'Tags': 'red_circle,fire,chart_with_upwards_trend'
        }
        
        response = requests.post(url, data=final_report.encode('utf-8'), headers=headers, timeout=30)
        print(f"✅ Sent {symbol} notification: {response.status_code}")
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ Error sending {symbol}: {e}")
        return False

def is_market_hours():
    """Check if current time is during market hours (9 AM - 4 PM EST, Monday-Friday)"""
    # If testing mode is enabled, always return True
    if TESTING_MODE:
        logger = logging.getLogger(__name__)
        logger.info("🧪 TESTING MODE: Ignoring market hours (works on weekends)")
        return True
    
    # Define EST timezone
    est = pytz.timezone('US/Eastern')
    now = datetime.now(est)
    
    # Special case: Extended Saturday testing for 8-2-25 only (until 11:59 PM)
    if now.date() == datetime(2025, 8, 2).date() and now.weekday() == 5:  # Saturday 8-2-25
        extended_open = now.replace(hour=20, minute=0, second=0, microsecond=0)  # 8:00 PM
        extended_close = now.replace(hour=23, minute=59, second=0, microsecond=0)  # 11:59 PM
        if extended_open <= now <= extended_close:
            logger = logging.getLogger(__name__)
            logger.info("🎯 SPECIAL: Extended Saturday testing (8-2-25) 8:00 PM - 11:59 PM EST")
            return True
    
    # Check if it's a weekday (Monday=0, Sunday=6)
    if now.weekday() >= 5:  # Saturday or Sunday
        return False
    
    # Check if it's between 9 AM and 4 PM EST
    market_open = now.replace(hour=9, minute=0, second=0, microsecond=0)
    market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)
    
    return market_open <= now <= market_close

def run_analysis_with_timeout():
    """Run analysis and automatically stop after 2 minutes"""
    logger = logging.getLogger(__name__)
    
    if not is_market_hours():
        logger.info("⏰ Outside market hours - skipping analysis")
        return
    
    # Flag to control analysis duration
    analysis_running = [True]
    
    def timeout_handler():
        """Stop analysis after 2 minutes"""
        time.sleep(120)  # 2 minutes = 120 seconds
        analysis_running[0] = False
        logger.info("⏱️ 2-minute timeout reached - stopping analysis")
    
    def run_analysis():
        """Run the actual analysis"""
        try:
            logger.info("🚀 Starting 15-minute comprehensive multi-stock analysis...")
            
            # Use comprehensive analyzer for detailed multi-stock analysis
            comprehensive_analyzer = ComprehensiveOptionsAnalyzer()
            results = comprehensive_analyzer.analyze_all_stocks()
            
            if results:
                # Generate comprehensive reports for each stock
                stock_reports = comprehensive_analyzer.create_comprehensive_report(results)
                
                # Send via ntfy
                try:
                    import config
                    if hasattr(config, 'NOTIFICATION_CONFIG'):
                        ntfy_config = config.NOTIFICATION_CONFIG.get('ntfy', {})
                        if ntfy_config.get('enabled', True):
                            topic = ntfy_config.get('topic', 'options_price')
                            
                            # Send multi-stock notifications (3 minutes apart)
                            send_multi_stock_notifications(stock_reports, topic)
                            
                            stocks_analyzed = list(stock_reports.keys())
                            logger.info("✅ Comprehensive analysis completed and notifications sent!")
                            logger.info(f"📊 Analyzed: {', '.join(stocks_analyzed)}")
                            logger.info("💰 Resource usage: ~2-4 minutes per stock (multi-stock detailed analysis)")
                            logger.info(f"⏱️ Total notification time: ~{len(stocks_analyzed) * 3} minutes (3 min apart)")
                except Exception as notification_error:
                    # No fallback - comprehensive system is required
                    logger.error(f"Detailed notification failed: {notification_error}")
                    logger.error("❌ No fallback analyzer available")
                    # Mark analysis as complete
                    analysis_running[0] = False
                    return False
            else:
                logger.error("❌ Comprehensive analysis failed - no results")
                # Mark analysis as complete
                analysis_running[0] = False
                return False
                
        except Exception as e:
            logger.error(f"💥 Error during comprehensive analysis: {e}")
            logger.error("❌ No fallback analyzer available")
            # Mark analysis as complete
            analysis_running[0] = False
            return False
        
        # Mark analysis as complete
        analysis_running[0] = False
        return True
    
    # Start timeout timer in background
    timeout_thread = threading.Thread(target=timeout_handler)
    timeout_thread.daemon = True
    timeout_thread.start()
    
    # Start analysis in background
    analysis_thread = threading.Thread(target=run_analysis)
    analysis_thread.daemon = True
    analysis_thread.start()
    
    # Wait for either analysis to complete or timeout
    start_time = time.time()
    while analysis_running[0]:
        elapsed = time.time() - start_time
        if elapsed >= 120:  # 2 minutes max
            break
        time.sleep(1)
    
    elapsed_time = time.time() - start_time
    logger.info(f"🏁 Analysis session completed in {elapsed_time:.1f} seconds")
    logger.info("💤 Entering sleep mode until next hour...")

def get_next_run_time():
    """Calculate when the next analysis should run"""
    est = pytz.timezone('US/Eastern')
    now = datetime.now(est)
    
    # Next run is at the top of the next hour
    next_hour = now.replace(minute=0, second=0, microsecond=0)
    if now.minute > 0 or now.second > 0:
        next_hour = next_hour.replace(hour=next_hour.hour + 1)
    
    # Handle day rollover
    if next_hour.hour >= 24:
        next_hour = next_hour.replace(hour=0, day=next_hour.day + 1)
    
    return next_hour

def main():
    """Main function for efficient analyzer"""
    logger = setup_logging()
    
    if TESTING_MODE:
        logger.info("🧪 TESTING MODE ENABLED - Will run on weekends")
        logger.info("🔧 Remember to set TESTING_MODE = False for production")
    
    logger.info("⚡ Starting Efficient NVDA Options Analyzer")
    logger.info("⏰ Schedule: 2 minutes every hour (14 min/day total)")
    logger.info("💰 Resource savings: 97% less usage vs continuous running")
    logger.info("📊 Monthly usage: ~7 hours (vs 210 hours continuous)")
    
    # Check if config exists
    try:
        import config
        logger.info("✅ Configuration loaded successfully")
    except ImportError:
        logger.warning("⚠️ Configuration not found - using defaults")
    
    # Run initial analysis if in market hours
    logger.info("🎯 Running initial analysis...")
    run_analysis_with_timeout()
    
    try:
        while True:
            # Calculate next run time
            next_run = get_next_run_time()
            now = datetime.now(pytz.timezone('US/Eastern'))
            sleep_seconds = (next_run - now).total_seconds()
            
            if sleep_seconds <= 0:
                sleep_seconds = 3600  # 1 hour fallback
            
            logger.info(f"💤 Sleeping until {next_run.strftime('%H:%M:%S EST')} ({sleep_seconds/60:.1f} minutes)")
            
            # Sleep until next hour
            time.sleep(sleep_seconds)
            
            # Run the analysis burst
            run_analysis_with_timeout()
            
    except KeyboardInterrupt:
        logger.info("👋 Efficient analyzer stopped by user")
    except Exception as e:
        logger.error(f"💥 Error: {e}")

if __name__ == "__main__":
    main()

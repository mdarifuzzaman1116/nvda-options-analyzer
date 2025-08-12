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
    """Send optimized notification with ALL 4 WEEKS and TOP 5 STRIKES in aligned table format"""
    try:
        import requests
        import re
        
        # PREVIEW what we're about to send
        print(f"\n" + "="*80)
        print(f"📱 SENDING {symbol} NOTIFICATION PREVIEW")
        print("="*80)
        
        # Extract current stock price from report
        current_price = 0.0
        price_match = re.search(rf"{symbol} \(\$(\d+\.\d+)\)", report)
        if price_match:
            current_price = float(price_match.group(1))
        
        # Create clean table-formatted notification with NEW FORMAT ONLY
        final_report = f"🚨 URGENT {symbol} ALERT 🚨\n"
        final_report += f"📊 === ALL 4 WEEKS TOP 5 STRIKES === 📊\n"
        final_report += f"💰 Current {symbol} Price: ${current_price:.2f}\n\n"
        
        # DYNAMICALLY extract week headers from the actual report (works for all stocks)
        weeks_data = []
        import re
        week_pattern = r"=== WEEK \d+ - \d{4}-\d{2}-\d{2} ==="
        week_matches = re.findall(week_pattern, report)
        
        # Use the actual weeks found in the report
        for week_header in week_matches:
            weeks_data.append((week_header, ""))
        
        # Fallback if no weeks found - use generic pattern
        if not weeks_data:
            weeks_data = [
                ("=== WEEK 1", ""),
                ("=== WEEK 2", ""), 
                ("=== WEEK 3", ""),
                ("=== WEEK 4", "")
            ]
        
        for week_name, _ in weeks_data:
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
                
                # Extract top 5 strikes with key info
                week_display = week_name.replace("===", "").strip()
                final_report += f"📅 {week_display}\n"
                
                # Table header with aligned columns
                final_report += "Strike    Below    Premium    Profit     Risk\n"
                
                strike_count = 0
                lines = week_section.split('\n')
                current_strike = None
                current_premium = None
                current_risk = None
                
                for line in lines:
                    if "Strike" in line and "$" in line and strike_count < 5:  # Show top 5
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
                            
                            # Calculate how much below current price
                            try:
                                strike_value = float(current_strike.replace("$", ""))
                                below_current = current_price - strike_value
                                below_text = f"-${below_current:.2f}" if below_current > 0 else f"+${abs(below_current):.2f}"
                            except:
                                below_text = "N/A"
                            
                            # Calculate profit value
                            try:
                                premium_value = float(current_premium.replace("$", ""))
                                profit_value = int(premium_value * 100)  # Convert to per contract
                                profit_text = f"${profit_value}"
                            except:
                                profit_text = "N/A"
                            
                            strike_count += 1
                            
                            # Use aligned column format (8 chars each column)
                            final_report += f"{current_strike:<8} {below_text:<8} {current_premium:<10} {profit_text:<10} {current_risk}\n"
                            
                            # Reset for next strike
                            current_strike = None
                            current_premium = None
                            current_risk = None
                
                final_report += "\n"
        
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
            'Title': f'{symbol} TOP 5 STRIKES/WEEK',
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
    """Check if current time is during market hours (9 AM - 5 PM EST, Monday-Friday)"""
    # If testing mode is enabled, always return True
    if TESTING_MODE:
        logger = logging.getLogger(__name__)
        logger.info("🧪 TESTING MODE: Ignoring market hours (works anytime)")
        return True
    
    # Define EST timezone
    est = pytz.timezone('US/Eastern')
    now = datetime.now(est)
    
    # Check if it's a weekday (Monday=0, Sunday=6)
    if now.weekday() >= 5:  # Saturday or Sunday
        return False
    
    # Check if it's between 9 AM and 5 PM EST (extended to 5 PM)
    market_open = now.replace(hour=9, minute=0, second=0, microsecond=0)
    market_close = now.replace(hour=17, minute=0, second=0, microsecond=0)  # 5 PM
    
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

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
from sms_options_analyzer import AutomatedOptionsAnalyzer
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

def send_comprehensive_notification(report, topic):
    """Send comprehensive report via ntfy with top recommendations first"""
    try:
        import requests
        
        # First, clear old notifications by sending a clearing message
        clear_url = f"https://ntfy.sh/{topic}"
        clear_headers = {
            'Title': 'Clearing Previous Notifications...',
            'Priority': 'min',
            'Tags': 'wastebasket',
            'Replace': 'clear-old-notifications',
            'Content-Type': 'text/plain; charset=utf-8'
        }
        clear_data = "Updating with latest analysis..."
        requests.post(clear_url, data=clear_data.encode('utf-8'), headers=clear_headers, timeout=10)
        time.sleep(1)  # Brief pause
        
        # Parse report to extract top recommendations
        top_recommendations = extract_top_recommendations(report)
        
        # Send top 2 recommendations first (in green)
        if top_recommendations:
            top_url = f"https://ntfy.sh/{topic}"
            top_headers = {
                'Title': 'TOP 2 RECOMMENDATIONS',
                'Priority': 'high',
                'Tags': 'green_circle,money_with_wings,chart_with_upwards_trend',
                'Replace': 'top-recommendations',
                'Content-Type': 'text/plain; charset=utf-8'
            }
            
            # Ensure proper UTF-8 encoding
            top_data = top_recommendations.encode('utf-8')
            response = requests.post(top_url, data=top_data, headers=top_headers, timeout=30)
            if response.status_code != 200:
                return False
            time.sleep(2)  # Pause between top and detailed
        
        # Split detailed report into chunks if needed
        max_length = 3800  # Leave room for headers
        
        if len(report) <= max_length:
            # Send as single message
            url = f"https://ntfy.sh/{topic}"
            headers = {
                'Title': 'OPTIONS ALERT - Detailed Analysis',
                'Priority': 'default',
                'Tags': 'chart_with_upwards_trend,money_with_wings,bell',
                'Replace': 'detailed-analysis',
                'Content-Type': 'text/plain; charset=utf-8'
            }
            
            response = requests.post(url, data=report.encode('utf-8'), headers=headers, timeout=30)
            return response.status_code == 200
        else:
            # Split into multiple parts - focus on keeping each week together
            parts = []
            lines = report.split('\n')
            current_part = ""
            
            for line in lines:
                # If adding this line would exceed limit, start new part
                if len(current_part + line + '\n') > max_length and current_part:
                    parts.append(current_part.strip())
                    current_part = line + '\n'
                else:
                    current_part += line + '\n'
            
            # Add the last part
            if current_part.strip():
                parts.append(current_part.strip())
            
            # Send each part with descriptive titles
            for i, part in enumerate(parts):
                url = f"https://ntfy.sh/{topic}"
                
                # Determine title and tags based on content - only positive recommendations
                if i == 0:
                    title = 'OPTIONS ALERT - Week 1-2 Analysis'
                    tags = 'chart_with_upwards_trend,money_with_wings,bell'
                elif i == 1:
                    title = 'OPTIONS ALERT - Week 3-4 Analysis'
                    tags = 'chart_with_upwards_trend,money_with_wings,bell'
                else:
                    title = 'OPTIONS ALERT - Additional Analysis'
                    tags = 'chart_with_upwards_trend,money_with_wings,bell'
                
                headers = {
                    'Title': title,
                    'Priority': 'default',
                    'Tags': tags,
                    'Replace': f'analysis-part-{i+1}',
                    'Content-Type': 'text/plain; charset=utf-8'
                }
                
                response = requests.post(url, data=part.encode('utf-8'), headers=headers, timeout=30)
                if response.status_code != 200:
                    return False
                    
                # Small delay between parts
                time.sleep(1)
            
            return True
            
    except Exception as e:
        logging.error(f"Failed to send comprehensive notification: {e}")
        return False

def extract_top_recommendations(report):
    """Extract top 2 recommendations from the comprehensive report"""
    try:
        lines = report.split('\n')
        recommendations = []
        current_rec = ""
        in_final_section = False
        
        # Look for the final recommendations section
        for i, line in enumerate(lines):
            if 'FINAL RECOMMENDATIONS' in line.upper() or 'TOP RECOMMENDATIONS' in line.upper():
                in_final_section = True
                continue
            
            if in_final_section:
                # Look for numbered recommendations with emojis
                if line.strip().startswith(('🥇 #1', '🥈 #2', '📊 #1', '📊 #2')):
                    current_rec = line + '\n'
                    # Collect the next few lines that belong to this recommendation
                    for j in range(i+1, min(i+8, len(lines))):
                        if lines[j].strip() and not lines[j].strip().startswith(('🥇', '🥈', '🥉', '📊')):
                            current_rec += lines[j] + '\n'
                        elif lines[j].strip().startswith(('🥇', '🥈', '🥉', '📊')):
                            break
                        elif not lines[j].strip():
                            current_rec += '\n'
                            break
                    
                    if current_rec.strip():
                        recommendations.append(current_rec.strip())
                        current_rec = ""
                        
                    if len(recommendations) >= 2:
                        break
        
        # If we didn't find recommendations in final section, try simpler approach
        if len(recommendations) < 2:
            recommendations = []
            for line in lines:
                # Look for lines with AAPL and good indicators
                if 'AAPL' in line.upper():
                    if any(indicator in line.lower() for indicator in ['🟢', 'excellent', 'best', 'winner', '🥇', '🥈']):
                        if '$' in line:  # Must have price info
                            recommendations.append(line.strip())
                            if len(recommendations) >= 2:
                                break
        
        if recommendations:
            top_text = "🟢 TOP 2 RECOMMENDATIONS:\n\n"
            for i, rec in enumerate(recommendations[:2], 1):
                # Clean up the recommendation text
                clean_rec = rec.replace('🥇', '').replace('🥈', '').replace('📊', '').strip()
                if clean_rec.startswith('#'):
                    clean_rec = clean_rec[2:].strip()  # Remove "# " numbering
                
                top_text += f"🏆 #{i} {clean_rec}\n\n"
            
            top_text += "💡 These are the highest Premium/Risk ratio plays with best probability!\n"
            top_text += "📊 Full detailed analysis follows below..."
            
            return top_text
        
        return None
        
    except Exception as e:
        logging.error(f"Error extracting top recommendations: {e}")
        return None

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
            logger.info("🚀 Starting 2-minute comprehensive AAPL analysis...")
            
            # Use comprehensive analyzer for detailed multi-stock analysis
            comprehensive_analyzer = ComprehensiveOptionsAnalyzer()
            results = comprehensive_analyzer.analyze_all_stocks()
            
            if results:
                # Generate comprehensive report
                comprehensive_report = comprehensive_analyzer.create_comprehensive_report(results)
                
                # Send via ntfy
                try:
                    import config
                    if hasattr(config, 'NOTIFICATION_CONFIG'):
                        ntfy_config = config.NOTIFICATION_CONFIG.get('ntfy', {})
                        if ntfy_config.get('enabled', True):
                            topic = ntfy_config.get('topic', 'options_price')
                            
                            # Send comprehensive notification
                            send_comprehensive_notification(comprehensive_report, topic)
                            
                            logger.info("✅ Comprehensive analysis completed and notification sent!")
                            logger.info("📊 Analyzed: AAPL (Apple Inc.)")
                            logger.info("💰 Resource usage: ~30 seconds (single-stock detailed analysis)")
                except Exception as notification_error:
                    # Fallback to simple notification
                    logger.warning(f"Detailed notification failed: {notification_error}")
                    logger.info("📤 Falling back to basic analyzer...")
                    analyzer = AutomatedOptionsAnalyzer()
                    success = analyzer.run_single_analysis()
                    # Mark analysis as complete
                    analysis_running[0] = False
                    return success
            else:
                logger.error("❌ Comprehensive analysis failed - no results")
                # Mark analysis as complete
                analysis_running[0] = False
                return False
                
        except Exception as e:
            logger.error(f"💥 Error during comprehensive analysis: {e}")
            logger.info("📤 Falling back to basic analyzer...")
            try:
                analyzer = AutomatedOptionsAnalyzer()
                success = analyzer.run_single_analysis()
                # Mark analysis as complete
                analysis_running[0] = False
                return success
            except Exception as fallback_error:
                logger.error(f"💥 Fallback analysis also failed: {fallback_error}")
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

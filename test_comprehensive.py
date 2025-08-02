#!/usr/bin/env python3
"""
Test the comprehensive multi-stock options analyzer
"""

import os
import sys
import logging
import requests
import time
from datetime        if best_choice_section.strip():
            # Add a nice header and footer for the notification
            top_text = "🚨 URGENT OPTIONS ALERT 🚨\n\n"
            top_text += best_choice_section.strip()
            top_text += "\n\n💡 This is the TOP recommendation across all timeframes!"
            top_text += "\n📊 Full detailed analysis follows below..."
            
            return top_textdatetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our analyzers
from comprehensive_analyzer import ComprehensiveOptionsAnalyzer

def setup_logging():
    """Setup logging for test"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    return logging.getLogger(__name__)

def send_comprehensive_notification(stock_reports, topic):
    """Send comprehensive report via ntfy with top recommendations first"""
    try:
        # Create a combined report from all stocks for the detailed analysis
        combined_report = ""
        for symbol in ['AAPL', 'NVDA', 'GOOG', 'GOOGL']:
            if symbol in stock_reports:
                combined_report += stock_reports[symbol] + "\n\n" + "="*50 + "\n\n"
        
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
        top_recommendations = extract_top_recommendations(stock_reports)
        
        # Send top recommendation first (in red for urgency)
        if top_recommendations:
            top_url = f"https://ntfy.sh/{topic}"
            top_headers = {
                'Title': '🥇 ABSOLUTE BEST CHOICE (TEST)',
                'Priority': 'urgent',
                'Tags': 'red_circle,money_with_wings,chart_with_upwards_trend,fire',
                'Replace': 'absolute-best-choice-test',
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
        
        if len(combined_report) <= max_length:
            # Send as single message
            url = f"https://ntfy.sh/{topic}"
            headers = {
                'Title': 'OPTIONS ALERT - Detailed Analysis (TEST)',
                'Priority': 'default',
                'Tags': 'chart_with_upwards_trend,money_with_wings,bell',
                'Replace': 'detailed-analysis-test',
                'Content-Type': 'text/plain; charset=utf-8'
            }
            
            response = requests.post(url, data=combined_report.encode('utf-8'), headers=headers, timeout=30)
            return response.status_code == 200
        else:
            # Split into multiple parts
            parts = []
            lines = combined_report.split('\n')
            current_part = ""
            
            for line in lines:
                if len(current_part + line + '\n') > max_length and current_part:
                    parts.append(current_part.strip())
                    current_part = line + '\n'
                else:
                    current_part += line + '\n'
            
            if current_part.strip():
                parts.append(current_part.strip())
            
            # Send each part
            for i, part in enumerate(parts):
                url = f"https://ntfy.sh/{topic}"
                
                if i == 0:
                    title = 'OPTIONS ALERT - Week 1-2 Analysis (TEST)'
                    tags = 'chart_with_upwards_trend,money_with_wings,bell'
                elif i == 1:
                    title = 'OPTIONS ALERT - Week 3-4 Analysis (TEST)'
                    tags = 'chart_with_upwards_trend,money_with_wings,bell'
                else:
                    title = 'OPTIONS ALERT - Additional Analysis (TEST)'
                    tags = 'chart_with_upwards_trend,money_with_wings,bell'
                
                headers = {
                    'Title': title,
                    'Priority': 'default',
                    'Tags': tags,
                    'Replace': f'analysis-test-part-{i+1}',
                    'Content-Type': 'text/plain; charset=utf-8'
                }
                
                response = requests.post(url, data=part.encode('utf-8'), headers=headers, timeout=30)
                if response.status_code != 200:
                    return False
                time.sleep(1)
            
            return True
            
    except Exception as e:
        logging.error(f"Failed to send comprehensive notification: {e}")
        return False

def extract_top_recommendations(stock_reports):
    """Extract the ABSOLUTE BEST CHOICE section from the comprehensive report"""
    try:
        # Get the AAPL report as it's the main focus
        if 'AAPL' not in stock_reports:
            return None
            
        report = stock_reports['AAPL']
        lines = report.split('\n')
        best_choice_section = ""
        in_best_choice = False
        
        # Look for the ABSOLUTE BEST CHOICE section
        for i, line in enumerate(lines):
            if '⭐ === ABSOLUTE BEST CHOICE === ⭐' in line:
                in_best_choice = True
                best_choice_section = line + '\n'
                continue
            
            if in_best_choice:
                # Continue collecting lines until we hit the next major section
                if line.strip().startswith('🏆 === WEEKLY BEST PICKS'):
                    break
                else:
                    best_choice_section += line + '\n'
        
        if best_choice_section.strip():
            # Add a nice header and footer for the notification
            top_text = "� URGENT OPTIONS ALERT 🚨\n\n"
            top_text += best_choice_section.strip()
            top_text += "\n\n💡 This is the TOP recommendation across all timeframes!"
            top_text += "\n📊 Full detailed analysis follows below..."
            
            return top_text
        
        return None
        
    except Exception as e:
        logging.error(f"Error extracting top recommendations: {e}")
        return None

def main():
    """Test the comprehensive analyzer"""
    logger = setup_logging()
    
    logger.info("🧪 TESTING Comprehensive AAPL Options Analyzer")
    logger.info("📊 Analyzing: AAPL (Apple Inc.)")
    
    try:
        # Create analyzer
        logger.info("🚀 Starting comprehensive analysis...")
        comprehensive_analyzer = ComprehensiveOptionsAnalyzer()
        
        # Run analysis
        results = comprehensive_analyzer.analyze_all_stocks()
        
        if results:
            logger.info(f"✅ Analysis completed! Got {len(results)} AAPL analysis")
            
            # Generate comprehensive report
            comprehensive_report = comprehensive_analyzer.create_comprehensive_report(results)
            
            # Send notification
            try:
                import config
                if hasattr(config, 'NOTIFICATION_CONFIG'):
                    ntfy_config = config.NOTIFICATION_CONFIG.get('ntfy', {})
                    if ntfy_config.get('enabled', True):
                        topic = ntfy_config.get('topic', 'options_price')
                        
                        logger.info("📤 Sending comprehensive notification...")
                        success = send_comprehensive_notification(comprehensive_report, topic)
                        
                        if success:
                            logger.info("✅ Comprehensive notification sent successfully!")
                            logger.info(f"📱 Check your ntfy app for topic: {topic}")
                        else:
                            logger.error("❌ Failed to send notification")
                else:
                    logger.warning("⚠️ No notification config found")
            except Exception as notification_error:
                logger.error(f"💥 Notification error: {notification_error}")
        else:
            logger.error("❌ Comprehensive analysis failed - no results")
            
    except Exception as e:
        logger.error(f"💥 Error during analysis: {e}")

if __name__ == "__main__":
    main()

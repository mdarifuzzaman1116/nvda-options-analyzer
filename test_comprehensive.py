#!/usr/bin/env python3
"""
Test the comprehensive multi-stock options analyzer
"""

import os
import sys
import logging
import requests
import time
from datetime import datetime

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

def send_comprehensive_notification(report, topic):
    """Send comprehensive report via ntfy with top recommendations first"""
    try:
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
                'Title': 'TOP 2 RECOMMENDATIONS (TEST)',
                'Priority': 'high',
                'Tags': 'green_circle,money_with_wings,chart_with_upwards_trend',
                'Replace': 'top-recommendations-test',
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
                'Title': 'OPTIONS ALERT - Detailed Analysis (TEST)',
                'Priority': 'default',
                'Tags': 'chart_with_upwards_trend,money_with_wings,bell',
                'Replace': 'detailed-analysis-test',
                'Content-Type': 'text/plain; charset=utf-8'
            }
            
            response = requests.post(url, data=report.encode('utf-8'), headers=headers, timeout=30)
            return response.status_code == 200
        else:
            # Split into multiple parts
            parts = []
            lines = report.split('\n')
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

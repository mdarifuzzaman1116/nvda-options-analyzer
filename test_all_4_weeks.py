#!/usr/bin/env python3
"""
Optimized test for AAPL options showing ALL 4 WEEKS in one notification
"""

import os
import sys
import logging
import requests
import time

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from comprehensive_analyzer import ComprehensiveOptionsAnalyzer

def setup_logging():
    """Set up logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def send_optimized_notification(aapl_report, topic="options_price"):
    """Send optimized AAPL notification with ALL 4 WEEKS visible"""
    try:
        # Extract ABSOLUTE BEST CHOICE
        absolute_best = ""
        if "⭐ === ABSOLUTE BEST CHOICE === ⭐" in aapl_report:
            start = aapl_report.find("⭐ === ABSOLUTE BEST CHOICE === ⭐")
            end = aapl_report.find("========================================", start)
            if end != -1:
                absolute_best = aapl_report[start:end].strip()
        
        # Extract WEEKLY SUMMARY (only once)
        weekly_summary = ""
        if "🏆 === WEEKLY BEST PICKS SUMMARY === 🏆" in aapl_report:
            start = aapl_report.find("🏆 === WEEKLY BEST PICKS SUMMARY === 🏆")
            end = aapl_report.find("============================================================", start)
            if end != -1:
                weekly_summary = aapl_report[start:end].strip()
        
        # Create condensed ALL 4 WEEKS detailed analysis
        condensed_weeks = "📊 === ALL 4 WEEKS TOP 10 STRIKES === 📊\n"
        
        # Extract key info for each week
        weeks_data = [
            ("WEEK 1 - 2025-08-08", "Days: 5"),
            ("WEEK 2 - 2025-08-15", "Days: 12"), 
            ("WEEK 3 - 2025-08-22", "Days: 19"),
            ("WEEK 4 - 2025-08-29", "Days: 26")
        ]
        
        for week_name, days_info in weeks_data:
            if week_name in aapl_report:
                week_start = aapl_report.find(week_name)
                # Find next week or end
                next_week_pos = len(aapl_report)
                for next_week, _ in weeks_data:
                    if next_week != week_name:
                        pos = aapl_report.find(next_week, week_start + 1)
                        if pos != -1 and pos < next_week_pos:
                            next_week_pos = pos
                
                week_section = aapl_report[week_start:next_week_pos]
                
                # Extract top 10 strikes with key info (closer to market price)
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
            final_report += "🚨 URGENT ALERT 🚨\n" + absolute_best + "\n\n"
        
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
        
        # PREVIEW
        print("\n" + "="*80)
        print("📱 TOP 10 STRIKES PER WEEK NOTIFICATION")
        print("="*80)
        print(f"Length: {len(final_report)} characters")
        print("-"*80)
        print(final_report)
        print("="*80)
        
        # Send notification
        url = f"https://ntfy.sh/{topic}"
        headers = {
            'Title': 'AAPL TOP 10 STRIKES/WEEK',
            'Priority': 'urgent',
            'Tags': 'red_circle,fire,chart_with_upwards_trend'
        }
        
        response = requests.post(url, data=final_report.encode('utf-8'), headers=headers, timeout=30)
        print(f"✅ Sent notification: {response.status_code}")
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Test the comprehensive analyzer with ALL 4 WEEKS"""
    logger = setup_logging()
    
    logger.info("🧪 TESTING AAPL Options - ALL 4 WEEKS VERSION")
    
    try:
        # Create analyzer
        logger.info("🚀 Starting analysis...")
        comprehensive_analyzer = ComprehensiveOptionsAnalyzer()
        
        # Run analysis
        results = comprehensive_analyzer.analyze_all_stocks()
        
        if results:
            logger.info(f"✅ Analysis completed! Got {len(results)} stocks")
            
            # Generate reports
            comprehensive_report = comprehensive_analyzer.create_comprehensive_report(results)
            
            if 'AAPL' in comprehensive_report:
                logger.info("📤 Sending optimized ALL 4 WEEKS notification...")
                success = send_optimized_notification(comprehensive_report['AAPL'])
            
            if success:
                logger.info("✅ Notification sent successfully!")
                logger.info("📱 Check your ntfy app for topic: options_price")
            else:
                logger.error("❌ Failed to send notification")
        else:
            logger.error("❌ No AAPL data found")
        
    except Exception as e:
        logger.error(f"❌ Error in main: {e}")

if __name__ == "__main__":
    main()

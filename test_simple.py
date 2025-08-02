#!/usr/bin/env python3
"""
Simple test for AAPL options with ABSOLUTE BEST CHOICE preservation
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

def send_simple_notification(stock_reports, topic):
    """Send AAPL report via ntfy with ABSOLUTE BEST CHOICE at the top of full report"""
    try:
        if 'AAPL' not in stock_reports:
            return False
            
        aapl_report = stock_reports['AAPL']
        
        # Extract ABSOLUTE BEST CHOICE section
        lines = aapl_report.split('\n')
        best_choice_section = ""
        remaining_report = ""
        in_best_choice = False
        found_best_choice = False
        
        for i, line in enumerate(lines):
            if 'ABSOLUTE BEST CHOICE' in line and not found_best_choice:
                in_best_choice = True
                found_best_choice = True
                best_choice_section = line + '\n'
                continue
            
            if in_best_choice:
                if line.strip().startswith('🏆 === WEEKLY BEST PICKS'):
                    # Start collecting the rest of the report from here
                    remaining_report = '\n'.join(lines[i:])
                    break
                else:
                    best_choice_section += line + '\n'
        
        # Create ONE comprehensive notification with ABSOLUTE BEST CHOICE at top
        if best_choice_section.strip():
            # Start with urgent alert header
            full_report = "*** URGENT AAPL ALERT ***\n\n"
            full_report += best_choice_section.strip() + "\n\n"
            full_report += "="*40 + "\n\n"
            
            # Add the detailed analysis but keep it concise
            if remaining_report:
                # Take first 2000 characters of detailed analysis
                detailed_preview = remaining_report[:2000]
                if len(remaining_report) > 2000:
                    # Find a good breaking point (end of a line)
                    last_newline = detailed_preview.rfind('\n')
                    if last_newline > 1500:  # Only break if we have substantial content
                        detailed_preview = detailed_preview[:last_newline]
                    detailed_preview += "\n\n... (Full analysis continues in app)"
                
                full_report += detailed_preview
        else:
            full_report = aapl_report[:3000]  # Fallback to first part of original report
        
        # PREVIEW what will be sent
        print("\n" + "="*80)
        print("� COMPLETE NOTIFICATION PREVIEW")
        print("="*80)
        print("Title: AAPL OPTIONS - BEST CHOICE + DETAILS")
        print("Priority: urgent")
        print("Tags: red_circle,money_with_wings,chart_with_upwards_trend,fire")
        print("-"*80)
        print("MESSAGE CONTENT:")
        print("-"*80)
        print(full_report[:1500] + "..." if len(full_report) > 1500 else full_report)
        print("-"*80)
        print(f"Total message length: {len(full_report)} characters")
        print("="*80)
        
        # Extract ABSOLUTE BEST CHOICE section
        absolute_best_section = ""
        print(f"🔍 Looking for ABSOLUTE BEST CHOICE in report...")
        
        # Look for various patterns that might contain the best choice
        patterns_to_check = [
            "🏆 ABSOLUTE BEST CHOICE:",
            "⭐ === ABSOLUTE BEST CHOICE === ⭐",
            "ABSOLUTE BEST CHOICE",
            "🥇 AAPL Week"
        ]
        
        for pattern in patterns_to_check:
            if pattern in aapl_report:
                print(f"✅ Found pattern: {pattern}")
                start_pos = aapl_report.find(pattern)
                # Find the end by looking for the next major section or end of text
                end_markers = ["\n\n📊", "\n\n🎯", "\n\n═", "\n\n===", "\n🏆 ==="]
                end_pos = len(aapl_report)
                
                for marker in end_markers:
                    marker_pos = aapl_report.find(marker, start_pos + 1)
                    if marker_pos != -1 and marker_pos < end_pos:
                        end_pos = marker_pos
                
                absolute_best_section = aapl_report[start_pos:end_pos].strip()
                print(f"📋 Extracted {len(absolute_best_section)} chars")
                break
        else:
            print("❌ No ABSOLUTE BEST CHOICE pattern found")
        
        # Send multiple notifications to ensure all details are visible
        url = f"https://ntfy.sh/{topic}"
        
        # 1. First notification: ABSOLUTE BEST CHOICE (urgent)
        if absolute_best_section:
            print(f"📤 Sending ABSOLUTE BEST CHOICE: {len(absolute_best_section)} chars")
            urgent_headers = {
                'Title': 'AAPL ABSOLUTE BEST CHOICE',
                'Priority': 'urgent',
                'Tags': 'red_circle,fire,star'
            }
            try:
                response1 = requests.post(url, data=absolute_best_section.encode('utf-8'), headers=urgent_headers, timeout=30)
                print(f"✅ Sent URGENT notification: {response1.status_code}")
            except Exception as e:
                print(f"❌ Error sending urgent notification: {e}")
            time.sleep(2)  # Small delay between notifications
        
        # 2. Send complete detailed analysis in chunks
        chunk_size = 3500  # Safe size for ntfy
        chunks = []
        
        for i in range(0, len(full_report), chunk_size):
            chunk = full_report[i:i + chunk_size]
            
            # Find last complete line if we're not at the end
            if i + chunk_size < len(full_report):
                last_newline = chunk.rfind('\n')
                if last_newline > 0:
                    chunk = chunk[:last_newline]
            
            chunks.append(chunk)
        
        # Send each chunk
        for idx, chunk in enumerate(chunks):
            chunk_headers = {
                'Title': f'AAPL DETAILS ({idx + 1}/{len(chunks)})',
                'Priority': 'default',
                'Tags': 'chart_with_upwards_trend,money_with_wings'
            }
            
            try:
                response = requests.post(url, data=chunk.encode('utf-8'), headers=chunk_headers, timeout=30)
                print(f"✅ Sent chunk {idx + 1}: {response.status_code} - {len(chunk)} chars")
            except Exception as e:
                print(f"❌ Error sending chunk {idx + 1}: {e}")
            
            if idx < len(chunks) - 1:  # Don't delay after last chunk
                time.sleep(1)  # Brief delay between chunks
        
        return True
            
    except Exception as e:
        logging.error(f"Failed to send notification: {e}")
        return False

def main():
    """Test the comprehensive analyzer"""
    logger = setup_logging()
    
    logger.info("🧪 TESTING AAPL Options with ABSOLUTE BEST CHOICE")
    
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
            
            # Send notification
            try:
                import config
                if hasattr(config, 'NOTIFICATION_CONFIG'):
                    ntfy_config = config.NOTIFICATION_CONFIG.get('ntfy', {})
                    if ntfy_config.get('enabled', True):
                        topic = ntfy_config.get('topic', 'options_price')
                        
                        logger.info("📤 Sending notification...")
                        success = send_simple_notification(comprehensive_report, topic)
                        
                        if success:
                            logger.info("✅ Notification sent successfully!")
                            logger.info(f"📱 Check your ntfy app for topic: {topic}")
                        else:
                            logger.error("❌ Failed to send notification")
                else:
                    logger.warning("⚠️ No notification config found")
            except Exception as notification_error:
                logger.error(f"💥 Notification error: {notification_error}")
        else:
            logger.error("❌ Analysis failed - no results")
            
    except Exception as e:
        logger.error(f"💥 Error during analysis: {e}")

if __name__ == "__main__":
    main()

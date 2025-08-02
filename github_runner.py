#!/usr/bin/env python3
"""
GitHub Actions Runner for AAPL Options Analysis
Designed for 2-minute bursts every hour to optimize resource usage
"""

import sys
import time
import logging
import os

def setup_logging():
    """Setup logging for GitHub Actions"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    return logging.getLogger(__name__)

def run_github_actions_analysis():
    """Run analysis optimized for GitHub Actions environment"""
    logger = setup_logging()
    
    logger.info("🚀 GitHub Actions AAPL Options Analysis Starting...")
    logger.info("⏰ 2-minute resource-optimized burst")
    logger.info("💰 Designed for 60-hour monthly limits")
    
    start_time = time.time()
    
    try:
        # Import our analyzer
        from comprehensive_analyzer import ComprehensiveOptionsAnalyzer
        
        logger.info("📊 Creating AAPL analyzer...")
        analyzer = ComprehensiveOptionsAnalyzer()
        
        logger.info("🔍 Fetching AAPL options data...")
        results = analyzer.analyze_all_stocks()
        
        if results:
            logger.info("📋 Generating comprehensive report...")
            report = analyzer.create_comprehensive_report(results)
            
            # Send notifications
            logger.info("📤 Sending notifications...")
            try:
                import config
                from efficient_analyzer import send_comprehensive_notification
                
                if hasattr(config, 'NOTIFICATION_CONFIG'):
                    ntfy_config = config.NOTIFICATION_CONFIG.get('ntfy', {})
                    if ntfy_config.get('enabled', True):
                        topic = ntfy_config.get('topic', 'options_price')
                        
                        success = send_comprehensive_notification(report, topic)
                        if success:
                            logger.info("✅ Notifications sent successfully!")
                        else:
                            logger.warning("⚠️ Notification sending failed")
                else:
                    logger.warning("⚠️ No notification config found")
                    
            except Exception as notify_error:
                logger.error(f"📤 Notification error: {notify_error}")
            
            duration = time.time() - start_time
            logger.info(f"🏁 Analysis completed in {duration:.1f} seconds")
            logger.info(f"📊 Report length: {len(report)} characters")
            logger.info("💤 GitHub Action will now terminate to save resources")
            
            return True
            
        else:
            logger.error("❌ No analysis results obtained")
            return False
            
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"💥 Analysis failed after {duration:.1f} seconds: {e}")
        return False

if __name__ == "__main__":
    success = run_github_actions_analysis()
    sys.exit(0 if success else 1)

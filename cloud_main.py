#!/usr/bin/env python3
"""
Cloud-ready version of the options analyzer
Optimized for Railway.app deployment
"""

import os
import sys
import time
import logging
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our analyzer
from sms_options_analyzer import AutomatedOptionsAnalyzer

def setup_cloud_logging():
    """Setup logging for cloud environment"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)  # Cloud platforms read from stdout
        ]
    )
    return logging.getLogger(__name__)

def main():
    """Main function for cloud deployment"""
    logger = setup_cloud_logging()
    logger.info("🚀 Starting cloud-based options analyzer...")
    
    # Check if config exists
    try:
        import config
        logger.info("✅ Configuration loaded successfully")
    except ImportError:
        logger.error("❌ Configuration not found!")
        logger.info("📝 Creating default configuration...")
        
        # Create default config for cloud
        config_content = '''
# Configuration for Options Analyzer
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
    
    # Start the analyzer
    try:
        analyzer = AutomatedOptionsAnalyzer()
        logger.info("🔄 Starting automated analysis...")
        analyzer.start_automation()
    except KeyboardInterrupt:
        logger.info("👋 Analyzer stopped by user")
    except Exception as e:
        logger.error(f"💥 Error: {e}")
        # In cloud, we want to restart on error
        logger.info("🔄 Restarting in 60 seconds...")
        time.sleep(60)
        main()  # Restart

if __name__ == "__main__":
    main()

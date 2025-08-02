#!/usr/bin/env python3
"""
Simple terminal test to verify system is working
"""

import sys
import os
import time
from datetime import datetime

print("🔧 Terminal Test Starting...")
print(f"📅 Current time: {datetime.now()}")
print(f"🐍 Python version: {sys.version}")
print(f"📂 Working directory: {os.getcwd()}")
print(f"📁 Files in directory: {len(os.listdir('.'))}")

# Test imports
try:
    import requests
    print("✅ requests module working")
except ImportError as e:
    print(f"❌ requests import failed: {e}")

try:
    import yfinance
    print("✅ yfinance module working")
except ImportError as e:
    print(f"❌ yfinance import failed: {e}")

try:
    from comprehensive_analyzer import ComprehensiveOptionsAnalyzer
    print("✅ comprehensive_analyzer import working")
except ImportError as e:
    print(f"❌ comprehensive_analyzer import failed: {e}")

try:
    import config
    print("✅ config import working")
    if hasattr(config, 'NOTIFICATION_CONFIG'):
        print("✅ NOTIFICATION_CONFIG found")
        ntfy_config = config.NOTIFICATION_CONFIG.get('ntfy', {})
        if ntfy_config.get('enabled', False):
            topic = ntfy_config.get('topic', 'options_price')
            print(f"✅ ntfy topic: {topic}")
        else:
            print("⚠️ ntfy not enabled in config")
    else:
        print("⚠️ NOTIFICATION_CONFIG not found")
except ImportError as e:
    print(f"❌ config import failed: {e}")

print("🏁 Terminal test completed!")

#!/usr/bin/env python3
"""
Test different notification formats to see how they appear on mobile
"""

import requests
import time

def test_mobile_formatting():
    """Test how notifications look on mobile devices"""
    topic = "options_price"
    
    print("📱 Testing mobile notification formatting...")
    print("🔔 Sending test notifications to ntfy.sh/options_price")
    print("=" * 50)
    
    # Test 1: Simple alert
    print("1️⃣ Sending simple alert...")
    simple_alert = "🚀 AAPL Alert: $202.38\n💰 Best Pick: $190 Strike → $226 profit\n⚠️ Risk: 19.1%"
    
    try:
        response = requests.post(
            f"https://ntfy.sh/{topic}",
            data=simple_alert.encode('utf-8'),
            headers={
                'Title': 'AAPL Options Alert',
                'Priority': 'high',
                'Tags': 'money_with_wings,chart_with_upwards_trend,bell',
                'Content-Type': 'text/plain; charset=utf-8'
            },
            timeout=10
        )
        print(f"   ✅ Status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    time.sleep(3)
    
    # Test 2: Rich notification with emojis
    print("2️⃣ Sending rich notification...")
    rich_alert = """🏆 TOP RECOMMENDATION
🥇 AAPL Week 4 - 2025-08-29
💰 Potential Profit: $2.26 or $226
🎯 Strike: $190 (19.1% risk)
⏰ Daily Decay: $0.087

🟡 Quality: GOOD
🚀 Total Contract Value: $226"""
    
    try:
        response = requests.post(
            f"https://ntfy.sh/{topic}",
            data=rich_alert.encode('utf-8'),
            headers={
                'Title': 'Best AAPL Put Option',
                'Priority': 'default',
                'Tags': 'trophy,green_circle,money_bag',
                'Content-Type': 'text/plain; charset=utf-8'
            },
            timeout=10
        )
        print(f"   ✅ Status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    time.sleep(3)
    
    # Test 3: Summary format
    print("3️⃣ Sending summary notification...")
    summary = """📊 WEEKLY SUMMARY (Aug 2)
⭐ Best: Week 4 - $226 profit
🟡 Good: Week 3 - $176 profit  
🟠 Fair: Week 2 - $160 profit
🟠 Fair: Week 1 - $112 profit

💡 All options under 20% risk
🎯 Current AAPL: $202.38"""
    
    try:
        response = requests.post(
            f"https://ntfy.sh/{topic}",
            data=summary.encode('utf-8'),
            headers={
                'Title': 'AAPL Weekly Summary',
                'Priority': 'default',
                'Tags': 'chart,money_with_wings,calendar',
                'Content-Type': 'text/plain; charset=utf-8'
            },
            timeout=10
        )
        print(f"   ✅ Status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n✅ Test notifications sent!")
    print("📱 Check your ntfy.sh/options_price page or mobile app")
    print(f"🌐 Web: https://ntfy.sh/{topic}")

if __name__ == "__main__":
    test_mobile_formatting()

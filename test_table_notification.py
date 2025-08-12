#!/usr/bin/env python3
"""
Test file to check if ntfy can handle table-formatted notifications
Testing different table formats to see what renders best on mobile
"""

import requests
import time

def test_table_formats():
    """Test different table formatting options with ntfy"""
    
    # Our ntfy topic
    topic = "options_price"
    url = f"https://ntfy.sh/{topic}"
    
    print("🧪 Testing different table formats with ntfy...")
    print("=" * 60)
    
    # Test 1: Simple ASCII table
    test1_data = """🚨 TEST 1: ASCII TABLE FORMAT 🚨

📊 AAPL OPTIONS - WEEK 1
┌─────────┬─────────┬──────────┬─────────┐
│ Strike  │ Premium │ Profit   │ Risk    │
├─────────┼─────────┼──────────┼─────────┤
│ $225    │ $1.24   │ $124     │ 16.5%   │
│ $220    │ $1.56   │ $156     │ 18.2%   │
│ $215    │ $2.01   │ $201     │ 22.1%   │
│ $210    │ $2.78   │ $278     │ 28.5%   │
└─────────┴─────────┴──────────┴─────────┘

⭐ BEST CHOICE: $220 Strike → $156 profit"""
    
    # Test 2: Markdown table format
    test2_data = """🚨 TEST 2: MARKDOWN TABLE FORMAT 🚨

📊 AAPL OPTIONS - WEEK 1

| Strike | Premium | Profit | Risk  |
|--------|---------|--------|-------|
| $225   | $1.24   | $124   | 16.5% |
| $220   | $1.56   | $156   | 18.2% |
| $215   | $2.01   | $201   | 22.1% |
| $210   | $2.78   | $278   | 28.5% |

⭐ BEST CHOICE: $220 Strike → $156 profit"""
    
    # Test 3: Simple aligned columns (no borders)
    test3_data = """🚨 TEST 3: ALIGNED COLUMNS FORMAT 🚨

📊 AAPL OPTIONS - WEEK 1

Strike    Premium    Profit     Risk
$225      $1.24      $124       16.5%
$220      $1.56      $156       18.2%
$215      $2.01      $201       22.1%
$210      $2.78      $278       28.5%

⭐ BEST CHOICE: $220 Strike → $156 profit"""
    
    # Test 4: Bullet point format with emojis
    test4_data = """🚨 TEST 4: EMOJI BULLET FORMAT 🚨

📊 AAPL OPTIONS - WEEK 1

🎯 $225 • $1.24 → $124 profit • 16.5% risk
🎯 $220 • $1.56 → $156 profit • 18.2% risk  
🎯 $215 • $2.01 → $201 profit • 22.1% risk
🎯 $210 • $2.78 → $278 profit • 28.5% risk

⭐ BEST CHOICE: $220 Strike → $156 profit"""
    
    # Test 5: Compact table with symbols
    test5_data = """🚨 TEST 5: COMPACT SYMBOL FORMAT 🚨

📊 AAPL OPTIONS - WEEK 1

Strike │ Premium │ Profit │ Risk
$225   │ $1.24   │ $124   │ 16.5%
$220   │ $1.56   │ $156   │ 18.2%
$215   │ $2.01   │ $201   │ 22.1%
$210   │ $2.78   │ $278   │ 28.5%

⭐ BEST CHOICE: $220 Strike → $156 profit"""
    
    tests = [
        ("ASCII Table", test1_data),
        ("Markdown Table", test2_data), 
        ("Aligned Columns", test3_data),
        ("Emoji Bullets", test4_data),
        ("Compact Symbols", test5_data)
    ]
    
    for i, (test_name, test_data) in enumerate(tests, 1):
        print(f"\n📱 Sending Test {i}: {test_name}")
        print("-" * 40)
        print(f"Length: {len(test_data)} characters")
        print("Preview:")
        print(test_data[:200] + "..." if len(test_data) > 200 else test_data)
        
        # Send notification
        headers = {
            'Title': f'Table Test {i}: {test_name}',
            'Priority': 'default',
            'Tags': 'test,table,format'
        }
        
        try:
            response = requests.post(url, data=test_data.encode('utf-8'), headers=headers, timeout=30)
            status = "✅ Sent" if response.status_code == 200 else "❌ Failed"
            print(f"{status} - Status: {response.status_code}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Wait 10 seconds between tests to avoid spam
        if i < len(tests):
            print("⏱️ Waiting 10 seconds before next test...")
            time.sleep(10)
    
    print("\n" + "=" * 60)
    print("🏁 All table format tests completed!")
    print("📱 Check your phone to see which format looks best")
    print("💡 Compare readability and choose the best option")

if __name__ == "__main__":
    test_table_formats()

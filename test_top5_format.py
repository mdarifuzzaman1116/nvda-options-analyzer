#!/usr/bin/env python3
"""
Test the new TOP 5 aligned table format
"""

import requests

def test_top5_table_format():
    """Test the new TOP 5 aligned table format"""
    
    # Sample data with current price
    current_price = 229.62
    symbol = "AAPL"
    
    # Create the notification with TOP 5 table format
    notification = f"""🚨 URGENT {symbol} ALERT 🚨
⭐ === ABSOLUTE BEST CHOICE === ⭐
🥇 AAPL Week 4 - $215 Strike → $378 profit

📊 === ALL 4 WEEKS TOP 5 STRIKES === 📊
💰 Current {symbol} Price: ${current_price:.2f}

📅 WEEK 1 - 2025-08-15 (3 days)
Strike    Below    Premium    Profit     Risk
$225      -$4.62   $0.99      $99        17.4%
$222      -$7.62   $1.25      $125       19.1%
$220      -$9.62   $1.43      $143       20.5%
$218      -$11.62  $1.65      $165       22.1%
$215      -$14.62  $2.01      $201       25.3%

📅 WEEK 2 - 2025-08-22 (10 days)
Strike    Below    Premium    Profit     Risk
$225      -$4.62   $1.58      $158       17.2%
$222      -$7.62   $1.83      $183       19.0%
$220      -$9.62   $2.05      $205       20.4%
$218      -$11.62  $2.31      $231       22.0%
$215      -$14.62  $2.73      $273       25.1%

📅 WEEK 3 - 2025-08-29 (17 days)
Strike    Below    Premium    Profit     Risk
$225      -$4.62   $2.02      $202       16.9%
$222      -$7.62   $2.34      $234       18.5%
$220      -$9.62   $2.58      $258       19.7%
$218      -$11.62  $2.86      $286       21.2%
$215      -$14.62  $3.28      $328       23.8%

📅 WEEK 4 - 2025-09-05 (24 days)
Strike    Below    Premium    Profit     Risk
$225      -$4.62   $2.35      $235       16.6%
$222      -$7.62   $2.71      $271       18.1%
$220      -$9.62   $2.98      $298       19.2%
$218      -$11.62  $3.31      $331       20.8%
$215      -$14.62  $3.78      $378       23.1%

⭐ BEST: Week 4 $215 → $378 profit (23.1% risk)"""

    print("🧪 Testing New TOP 5 Aligned Table Format")
    print("=" * 60)
    print(f"Length: {len(notification)} characters")
    print("-" * 60)
    print(notification)
    print("=" * 60)
    
    # Send the notification
    topic = "options_price"
    url = f"https://ntfy.sh/{topic}"
    headers = {
        'Title': f'{symbol} TOP 5 STRIKES/WEEK',
        'Priority': 'urgent',
        'Tags': 'test,table,top5,aapl'
    }
    
    try:
        response = requests.post(url, data=notification.encode('utf-8'), headers=headers, timeout=30)
        status = "✅ Sent" if response.status_code == 200 else "❌ Failed"
        print(f"\n{status} - Status: {response.status_code}")
        print("📱 Check your phone to see the new TOP 5 aligned table format!")
        print("🎯 More concise with the best 5 strikes per week")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_top5_table_format()

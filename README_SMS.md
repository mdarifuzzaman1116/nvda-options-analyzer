# 📱 FREE SMS Options Analyzer

Get your NVDA options analysis delivered directly to your phone via FREE text messages!

## 🆓 Free Notification Methods

### 1. 📧 Email-to-SMS (Completely Free)
- Works with all major US carriers
- Uses your phone carrier's email gateway
- Requires Gmail account (same as email version)
- **Carriers supported:** Verizon, AT&T, T-Mobile, Sprint, Boost, Cricket, US Cellular

### 2. 🔔 ntfy.sh (Completely Free)
- No signup required
- Install free "ntfy" app from App Store/Play Store
- Instant push notifications
- Works on phone and desktop

### 3. 💬 Discord Webhook (Free)
- Get notifications in Discord
- Free Discord account required
- Set up webhook in your server

### 4. 📲 Pushover (Premium)
- Most reliable notifications
- $5 one-time fee after free trial
- Professional notification service

## 🚀 Quick Start

1. **Setup SMS notifications:**
   ```bash
   python launch_sms.py
   # Choose option 1
   ```

2. **Start automated SMS alerts:**
   ```bash
   python launch_sms.py  
   # Choose option 2
   ```

## 📱 Sample Text Messages

### Short SMS (160 chars):
```
📈 NVDA $174 - Best: 2W $155P $1.70 (19.0% risk) 08/01 23:30
```

### Detailed Notification:
```
🎯 NVDA Options Analysis - 2025-08-01 23:30
Current Price: $173.72

💰 Best Premium Picks (<20% risk):
• 1-Week: $165P $1.16 (17.2%)
• 2-Week: $162P $1.70 (19.0%)  
• 3-Week: $160P $1.97 (18.3%)
• 4-Week: $155P $2.82 (18.2%)

🏆 Top Pick: 4-Week $155P $2.82
```

## 🔧 Setup Instructions

### Option 1: Email-to-SMS (Recommended)
1. Run `python setup_sms.py`
2. Enter your 10-digit phone number
3. Select your carrier (Verizon, AT&T, etc.)
4. Use same Gmail credentials as email version
5. Test message will be sent automatically

### Option 2: ntfy.sh (Easiest)
1. Download "ntfy" app from App Store
2. Choose a unique topic name (e.g., "john_options_2024")
3. Subscribe to that topic in the app
4. Configure in setup script
5. Instant notifications!

### Option 3: Discord
1. Create Discord server or use existing
2. Go to Server Settings > Integrations > Webhooks
3. Create webhook, copy URL
4. Enter URL in setup script

## 📁 Files Overview

- `launch_sms.py` - Main SMS launcher
- `setup_sms.py` - SMS notification setup
- `sms_options_analyzer.py` - Core SMS analyzer
- `config.py` - Your notification settings

## 📊 What You Get

**Every hour you'll receive:**
- Current stock price
- Best option for each week (1-4 weeks)
- Premium amounts and assignment risk
- Top overall recommendation
- Risk assessment

## ⚙️ Configuration

Edit `config.py` to customize:
```python
ANALYSIS_CONFIG = {
    'ticker': 'NVDA',      # Stock to analyze
    'price_range': 40,     # Range below current price
    'schedule_interval': 'hour'  # Frequency
}
```

## 🔍 Troubleshooting

### SMS Not Working?
1. **Check carrier:** Make sure you selected the right carrier
2. **Phone number:** Use 10 digits, no dashes/spaces
3. **Gmail app password:** Must be app password, not regular password
4. **Test manually:** Use option 5 in launcher to test

### ntfy Not Working?
1. **Topic name:** Must be unique, use letters/numbers only
2. **App subscription:** Make sure you subscribed to the exact topic
3. **Internet:** Both your computer and phone need internet

### Discord Not Working?
1. **Webhook URL:** Must be complete Discord webhook URL
2. **Permissions:** Make sure webhook has permission to post

## 📱 Carrier Email Gateways

| Carrier | Gateway |
|---------|---------|
| Verizon | @vtext.com |
| AT&T | @txt.att.net |
| T-Mobile | @tmomail.net |
| Sprint | @messaging.sprintpcs.com |
| Boost | @myboostmobile.com |
| Cricket | @sms.cricketwireless.net |

## 💡 Pro Tips

1. **Use ntfy.sh** for instant notifications
2. **Email-to-SMS** for simple text messages
3. **Test first** before starting automation
4. **Check logs** if notifications stop working
5. **Multiple methods** can be enabled simultaneously

## 🛑 Stopping

Press `Ctrl+C` in terminal to stop the analyzer.

## 🔒 Privacy

- Phone number stored locally only
- No data sent to third parties
- ntfy.sh is open source and privacy-focused
- Discord/email use your existing accounts

## 💰 Cost Breakdown

- **Email-to-SMS:** FREE (uses your existing phone plan)
- **ntfy.sh:** FREE forever
- **Discord:** FREE
- **Pushover:** $5 one-time (optional)

---

**Get started now:** `python launch_sms.py`

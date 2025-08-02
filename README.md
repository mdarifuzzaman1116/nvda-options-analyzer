# 🌩️ Cloud Deployment for NVDA Options Analyzer

An automated system that runs NVDA options analysis every hour in the cloud and sends notifications to your phone.

## 🚀 Free Cloud Deployment Options

### Option 1: Railway.app (Recommended)
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new)

**Setup Steps:**
1. Push this code to GitHub
2. Go to [Railway.app](https://railway.app) and sign up (free)
3. Create new project from GitHub repo
4. Railway auto-deploys and runs 24/7

**Cost:** $5 free credit monthly (enough for 24/7 operation)

### Option 2: GitHub Codespaces
1. Push to GitHub
2. Open in Codespaces
3. Run: `python sms_options_analyzer.py` in background

**Cost:** 60 hours/month free

### Option 3: Render.com
1. Connect GitHub repo
2. Deploy as "Background Worker"
3. Set start command: `python sms_options_analyzer.py`

**Cost:** 750 hours/month free

## 📱 Phone Notifications Setup

**No API keys needed!** Uses free ntfy.sh service:

1. **Install ntfy app** on your phone ([iOS](https://apps.apple.com/app/ntfy/id1625396347) | [Android](https://play.google.com/store/apps/details?id=io.heckel.ntfy))
2. **Subscribe** to topic: `options_price`
3. **Done!** You'll get hourly NVDA analysis

## �️ Local Development

You'll need a Gmail account with:
- 2-factor authentication enabled
- An "App Password" generated for this script

### Getting Gmail App Password:
1. Go to [Google Account Settings](https://myaccount.google.com/)
2. Security → 2-Step Verification
3. App passwords → Generate new password
4. Select "Mail" as the app
5. Use the 16-character password in the setup

## 🔧 Configuration Files

- `config.py` - Your personal configuration (created during setup)
- `config_template.py` - Template with all available options

## 📁 Files Overview

- `launch.py` - Easy launcher with menu options
- `setup_automation.py` - Interactive setup script
- `automated_options_analyzer.py` - Main automation script
- `nvda_puts.py` - Original manual analysis script

## ⏰ How It Works

1. **Scheduler runs every hour** (configurable)
2. **Fetches latest options data** for your chosen ticker
3. **Analyzes 1-4 week put options** with Greek calculations
4. **Emails you the results** with detailed analysis
5. **Logs everything** for troubleshooting

## 📊 What You Get in Email

- **Current stock price** and analysis time
- **All strike prices** in your range with:
  - Bid prices
  - Assignment probability (%)
  - Daily time decay ($)
- **Weekly recommendations**:
  - Best safe options (>$10 OTM)
  - Best premium options (<20% assignment risk)
- **Strategy recommendations**:
  - Conservative picks
  - Aggressive picks
  - Risk/reward analysis

## 🛠️ Customization

Edit `config.py` to change:
- Stock ticker to analyze
- Price range below current price
- How often to run analysis
- Email settings

## 📋 Commands

```bash
# Easy launcher (recommended)
python launch.py

# Direct commands
python setup_automation.py          # First-time setup
python automated_options_analyzer.py # Start automation
python nvda_puts.py NVDA 40         # Manual single run
```

## 🔍 Troubleshooting

1. **Check logs:** `tail -f options_analyzer.log`
2. **Test email:** Run setup again and send test email
3. **Check config:** Make sure `config.py` exists and has correct credentials
4. **Manual test:** Use launch.py option 3 for single run

## 📱 Stopping the System

Press `Ctrl+C` in the terminal running the automation to stop it.

## 🔒 Security

- Your email credentials are stored locally in `config.py`
- Use Gmail app passwords (not your main password)
- The script only reads market data and sends emails

## 🎯 Example Email Subject

```
📈 NVDA Options Analysis - 2025-08-01 15:30:00
```

## 💡 Tips

- Start with hourly analysis, adjust frequency as needed
- Keep the terminal window open or run in background
- Check logs regularly for any issues
- Test with a single run before starting automation

---

**Need help?** Check the logs or run a manual analysis first to test everything works.

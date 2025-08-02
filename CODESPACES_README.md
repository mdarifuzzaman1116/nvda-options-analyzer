# 🏦 NVDA Options Analyzer - GitHub Codespaces Deployment

Automated NVDA options analysis optimized for GitHub Codespaces free tier (60 hours/month).

## 🚀 Quick Start in Codespaces

1. **Open in Codespaces:**
   - Go to your GitHub repository
   - Click the green "Code" button
   - Select "Codespaces" tab
   - Click "Create codespace on main"

2. **Start the analyzer:**
   ```bash
   chmod +x start_codespaces.sh
   ./start_codespaces.sh
   ```

3. **Set up notifications:**
   - Install the ntfy app on your phone
   - Subscribe to topic: `options_price`
   - You'll receive hourly notifications during market hours!

## 📅 Schedule

- **Active hours:** Monday-Friday, 9 AM - 4 PM EST only
- **Frequency:** Every hour during market hours
- **Monthly usage:** ~35 hours (well within 60-hour free limit)

## 📱 Notifications

The system sends notifications via ntfy.sh with:
- Current NVDA price
- Best put options for each expiration week
- Assignment probabilities
- Auto-clearing (new notifications replace old ones)

## 💰 Cost Optimization

This setup is designed to maximize your GitHub Codespaces free tier:
- **Daily usage:** 7 hours (market hours only)
- **Monthly usage:** ~35 hours (5 days × 7 hours)
- **Free tier limit:** 60 hours/month
- **Buffer:** 25 hours remaining for other projects

## 🔧 Configuration

Edit `codespaces_config.py` to customize:
- Symbol to analyze (default: NVDA)
- Expiration weeks
- Notification settings
- Market hours

## 📊 How It Works

1. **Market Hours Detection:** Uses EST timezone to detect 9 AM - 4 PM weekdays
2. **Smart Scheduling:** Only runs during market hours to save resources
3. **Efficient Analysis:** Single analysis per hour instead of continuous running
4. **Auto-Stop:** Automatically stops outside market hours

## 🛠️ Manual Commands

- **Check status:** `ps aux | grep python`
- **View logs:** `tail -f analyzer.log` (if using background mode)
- **Stop manually:** `pkill -f market_hours_analyzer.py`

## 📱 ntfy Setup

1. Install ntfy app: [ntfy.sh](https://ntfy.sh)
2. Subscribe to topic: `options_price`
3. Enable notifications
4. You'll receive instant updates!

## 🔄 Updates

To update the code:
1. Commit changes to your GitHub repo
2. In Codespaces terminal: `git pull`
3. Restart: `./start_codespaces.sh`

---

*Optimized for market hours only - saves 65% of cloud resources!*

# GitHub Codespaces Configuration for NVDA Options Analyzer

# Trading configuration
SYMBOL = "NVDA"
EXPIRATION_WEEKS = [1, 2, 3, 4]  # Analyze puts expiring in these weeks

# Notification settings
NTFY_TOPIC = "options_price"
NTFY_URL = "https://ntfy.sh"

# Market hours (EST timezone)
MARKET_START_HOUR = 9   # 9 AM EST
MARKET_END_HOUR = 16    # 4 PM EST (market closes at 4 PM)
MARKET_TIMEZONE = "US/Eastern"

# Analysis settings for cloud optimization
MAX_ANALYSIS_TIME_MINUTES = 2  # Maximum time per analysis
ANALYSIS_FREQUENCY_MINUTES = 60  # Run every hour during market hours

# Debug settings
DEBUG_MODE = False
LOG_LEVEL = "INFO"

# Codespaces optimization
ESTIMATED_DAILY_HOURS = 7  # 9 AM to 4 PM = 7 hours
ESTIMATED_MONTHLY_HOURS = 35  # 7 hours × 5 days = 35 hours/month
FREE_TIER_LIMIT = 60  # GitHub Codespaces free tier limit

print(f"📊 Codespaces Configuration Loaded:")
print(f"   Daily usage: {ESTIMATED_DAILY_HOURS} hours (Market hours only)")
print(f"   Monthly usage: {ESTIMATED_MONTHLY_HOURS} hours")
print(f"   Free tier limit: {FREE_TIER_LIMIT} hours")
print(f"   Buffer remaining: {FREE_TIER_LIMIT - ESTIMATED_MONTHLY_HOURS} hours")
print(f"   Symbol: {SYMBOL}")
print(f"   Notification topic: {NTFY_TOPIC}")

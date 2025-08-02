# GitHub Codespaces Configuration for Efficient NVDA Options Analyzer

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

# Efficient analysis settings
MAX_ANALYSIS_TIME_MINUTES = 2  # Maximum 2 minutes per analysis burst
ANALYSIS_FREQUENCY_MINUTES = 60  # Run every hour during market hours
TESTING_MODE = True  # Enable for weekend testing (set False for production)

# Debug settings
DEBUG_MODE = False
LOG_LEVEL = "INFO"

# Codespaces optimization - MASSIVE SAVINGS!
ANALYSIS_DURATION_MINUTES = 2  # 2 minutes per hour
DAILY_ANALYSIS_SESSIONS = 7  # 9 AM to 4 PM = 7 sessions
DAILY_USAGE_MINUTES = ANALYSIS_DURATION_MINUTES * DAILY_ANALYSIS_SESSIONS  # 14 minutes
MONTHLY_USAGE_HOURS = (DAILY_USAGE_MINUTES * 22) / 60  # ~5.1 hours/month (22 trading days)
FREE_TIER_LIMIT = 60  # GitHub Codespaces free tier limit

print(f"⚡ Efficient Codespaces Configuration Loaded:")
print(f"   Analysis duration: {ANALYSIS_DURATION_MINUTES} minutes per hour")
print(f"   Daily sessions: {DAILY_ANALYSIS_SESSIONS} (market hours)")
print(f"   Daily usage: {DAILY_USAGE_MINUTES} minutes (vs 420 minutes continuous)")
print(f"   Monthly usage: {MONTHLY_USAGE_HOURS:.1f} hours (vs 154 hours continuous)")
print(f"   Free tier limit: {FREE_TIER_LIMIT} hours")
print(f"   Resource savings: {((420-DAILY_USAGE_MINUTES)/420)*100:.1f}% per day")
print(f"   Symbol: {SYMBOL}")
print(f"   Notification topic: {NTFY_TOPIC}")
if TESTING_MODE:
    print(f"   🧪 TESTING MODE: Works on weekends")
else:
    print(f"   📅 PRODUCTION MODE: Market hours only")

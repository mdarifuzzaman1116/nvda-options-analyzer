# Configuration file for Automated Options Analyzer
# Copy this file to config.py and customize your settings

# Email Configuration
EMAIL_CONFIG = {
    'from_email': 'your_email@gmail.com',    # Your Gmail address
    'to_email': 'recipient@gmail.com',       # Where to send the reports
    'app_password': 'your_app_password'      # Gmail app password (see setup instructions)
}

# Analysis Configuration
ANALYSIS_CONFIG = {
    'ticker': 'NVDA',           # Stock ticker to analyze
    'price_range': 40,          # Price range below current price to analyze
    'schedule_interval': 'hour' # How often to run: 'hour', 'day', '30minutes', etc.
}

# Email Settings
EMAIL_SETTINGS = {
    'send_emails': True,        # Set to False to disable emails (just log results)
    'attach_full_report': True, # Include detailed analysis as attachment
    'summary_only': False       # Send only summary (not full report)
}

# Logging Configuration
LOG_CONFIG = {
    'log_file': '/Users/mdarifuzzaman/Documents/puts/options_analyzer.log',
    'log_level': 'INFO'  # DEBUG, INFO, WARNING, ERROR
}

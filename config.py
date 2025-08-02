# SMS Options Analyzer Configuration
# Using ntfy.sh - No Gmail passwords needed!

NOTIFICATION_CONFIG = {'ntfy': {'enabled': True, 'topic': 'options_price'}}

ANALYSIS_CONFIG = {
    'ticker': 'AAPL',
    'price_range': 20.0,
    'schedule_interval': 'hour'
}

NOTIFICATION_SETTINGS = {
    'send_notifications': True,
    'notification_type': 'sms'
}

LOG_CONFIG = {
    'log_file': '/Users/mdarifuzzaman/Documents/puts/options_analyzer.log',
    'log_level': 'INFO'
}

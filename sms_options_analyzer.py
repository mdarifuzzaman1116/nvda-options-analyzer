import yfinance as yf
import pandas as pd
from datetime import datetime
import sys
import numpy as np
from py_vollib.black_scholes.greeks.analytical import delta, theta
from py_vollib.black_scholes import black_scholes
import warnings
import smtplib
import schedule
import time
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import json
import logging

warnings.filterwarnings('ignore')

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/Users/mdarifuzzaman/Documents/puts/options_analyzer.log'),
        logging.StreamHandler()
    ]
)

class AutomatedOptionsAnalyzer:
    def __init__(self, ticker_symbol="AAPL", price_range_below=30, notification_config=None):
        self.ticker_symbol = ticker_symbol.upper()
        self.price_range_below = price_range_below
        self.stock = None
        self.current_price = None
        self.notification_config = notification_config or {}
        
    def calculate_greeks(self, strike_price, current_price, time_to_expiry, implied_vol, risk_free_rate=0.05):
        """Calculate delta and theta for put options"""
        try:
            # Calculate delta for put option
            put_delta = delta('p', current_price, strike_price, time_to_expiry, risk_free_rate, implied_vol)
            
            # Calculate theta for put option  
            put_theta = theta('p', current_price, strike_price, time_to_expiry, risk_free_rate, implied_vol)
            
            return put_delta, put_theta
        except:
            return None, None
    
    def fetch_stock_data(self):
        """Fetch stock data with error handling"""
        try:
            logging.info(f"Fetching data for {self.ticker_symbol}...")
            self.stock = yf.Ticker(self.ticker_symbol)
            
            # Get current price
            hist = self.stock.history(period="1d")
            if hist.empty:
                raise ValueError(f"No price data available for {self.ticker_symbol}")
            
            self.current_price = hist["Close"].iloc[-1]
            logging.info(f"Current price: ${self.current_price:.2f}")
            return True
            
        except Exception as e:
            logging.error(f"Error fetching stock data: {e}")
            return False
    
    def get_time_to_expiry(self, expiration_date):
        """Calculate time to expiry in years"""
        try:
            exp_date = datetime.strptime(expiration_date, '%Y-%m-%d')
            current_date = datetime.now()
            days_to_expiry = (exp_date - current_date).days
            return max(days_to_expiry / 365.0, 1/365)  # Minimum 1 day
        except:
            return 0.02  # Default to ~7 days
    
    def analyze_puts(self, option_chain, expiration_date, simple_output=True):
        """Analyze put options within specified range"""
        puts = option_chain.puts
        
        # Calculate bounds - but get more strikes for analysis
        lower_bound = self.current_price - self.price_range_below
        upper_bound = self.current_price
        
        # Filter strike prices
        filtered_puts = puts[
            (puts['strike'] >= lower_bound) & 
            (puts['strike'] <= upper_bound)
        ].copy()
        
        if filtered_puts.empty:
            return None
        
        # Select base columns
        base_columns = ['strike', 'bid', 'impliedVolatility']
        available_columns = [col for col in base_columns if col in filtered_puts.columns]
        result = filtered_puts[available_columns].sort_values(by='strike', ascending=True)
        
        # Limit to top 20 strikes (closest to current price)
        result = result.tail(20)
        
        # Calculate time to expiry
        time_to_expiry = self.get_time_to_expiry(expiration_date)
        
        # Calculate Greeks for each option
        deltas = []
        thetas = []
        
        for _, row in result.iterrows():
            if 'impliedVolatility' in row and not pd.isna(row['impliedVolatility']) and row['impliedVolatility'] > 0:
                put_delta, put_theta = self.calculate_greeks(
                    row['strike'], 
                    self.current_price, 
                    time_to_expiry, 
                    row['impliedVolatility']
                )
                deltas.append(put_delta)
                thetas.append(put_theta)
            else:
                deltas.append(None)
                thetas.append(None)
        
        result['delta'] = deltas
        result['theta'] = thetas
        
        # Convert delta to assignment probability percentage (for puts, delta is negative)
        result['assignment_chance'] = result['delta'].apply(lambda x: abs(x * 100) if x is not None else None)
        
        # Convert theta to daily decay in dollars
        result['daily_decay'] = result['theta'].apply(lambda x: abs(x) if x is not None else None)
        
        # Calculate premium to risk ratio
        result['premium_risk_ratio'] = result.apply(
            lambda row: (row['bid'] / row['assignment_chance']) * 100 
            if row['assignment_chance'] is not None and row['assignment_chance'] > 0 
            else 0, axis=1
        )
        
        # Add expiration date for identification
        result['expiration'] = expiration_date
        
        return result
    
    def run_analysis_multi_expiration(self):
        """Run analysis for 1-week, 2-week, 3-week, and 4-week expirations"""
        if not self.fetch_stock_data():
            return False, "Failed to fetch stock data"
        
        # Check if options are available
        if not self.stock.options:
            return False, f"No options data available for {self.ticker_symbol}"
        
        results = {}
        
        # Define the expirations we want to analyze
        expiration_targets = [
            (0, "1-Week"),
            (1, "2-Week"), 
            (2, "3-Week"),
            (3, "4-Week")
        ]
        
        for index, week_label in expiration_targets:
            if index < len(self.stock.options):
                try:
                    exp_date = self.stock.options[index]
                    option_chain = self.stock.option_chain(exp_date)
                    result = self.analyze_puts(option_chain, exp_date, simple_output=True)
                    results[f"{week_label} Expiration ({exp_date})"] = result
                except Exception as e:
                    logging.error(f"Error getting {week_label} expiration: {e}")
            else:
                logging.warning(f"{week_label} expiration not available (only {len(self.stock.options)} expiration dates)")
        
        return True, results
    
    def create_sms_summary(self, results_dict):
        """Create a concise summary for SMS (160 character limit friendly)"""
        current_time = datetime.now().strftime('%m/%d %H:%M')
        
        # Find best options across all weeks
        all_premium_options = []
        
        for exp_name, result in results_dict.items():
            if result is not None and not result.empty:
                # Premium options (<20% assignment)
                premium_options = result[
                    (pd.notna(result['assignment_chance'])) &
                    (pd.notna(result['bid'])) &
                    (result['bid'] > 0) &
                    (result['assignment_chance'] < 20)
                ].copy()
                
                if not premium_options.empty:
                    best_premium = premium_options.nlargest(1, 'bid').iloc[0]
                    week_num = exp_name.split('-')[0]  # Extract "1" from "1-Week"
                    
                    all_premium_options.append({
                        'week': week_num,
                        'strike': best_premium['strike'],
                        'bid': best_premium['bid'],
                        'assignment_chance': best_premium['assignment_chance']
                    })
        
        if not all_premium_options:
            return f"📈 {self.ticker_symbol} ${self.current_price:.0f} - No suitable options found"
        
        # Find best option overall
        best_option = max(all_premium_options, key=lambda x: x['bid'])
        
        # Create SMS message (keeping it under 160 chars)
        sms_message = (
            f"📈 {self.ticker_symbol} ${self.current_price:.0f} - "
            f"Best: {best_option['week']}W ${best_option['strike']:.0f}P "
            f"${best_option['bid']:.2f} ({best_option['assignment_chance']:.1f}% risk) "
            f"{current_time}"
        )
        
        return sms_message
    
    def create_detailed_summary(self, results_dict):
        """Create detailed summary for longer notifications"""
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M')
        
        summary = f"🎯 {self.ticker_symbol} Options Analysis - {current_time}\n"
        summary += f"Current Price: ${self.current_price:.2f}\n\n"
        
        # Find best options for each week
        weekly_picks = []
        
        for exp_name, result in results_dict.items():
            if result is not None and not result.empty:
                # Premium options (<20% assignment)
                premium_options = result[
                    (pd.notna(result['assignment_chance'])) &
                    (pd.notna(result['bid'])) &
                    (result['bid'] > 0) &
                    (result['assignment_chance'] < 20)
                ].copy()
                
                if not premium_options.empty:
                    best_premium = premium_options.nlargest(1, 'bid').iloc[0]
                    week_label = exp_name.split(' ')[0]  # Extract "1-Week" part
                    
                    weekly_picks.append(
                        f"{week_label}: ${best_premium['strike']:.0f}P "
                        f"${best_premium['bid']:.2f} ({best_premium['assignment_chance']:.1f}%)"
                    )
        
        if weekly_picks:
            summary += "💰 Best Premium Picks (<20% risk):\n"
            for pick in weekly_picks:
                summary += f"• {pick}\n"
            
            # Find overall best
            all_options = []
            for exp_name, result in results_dict.items():
                if result is not None and not result.empty:
                    premium_options = result[
                        (pd.notna(result['assignment_chance'])) &
                        (pd.notna(result['bid'])) &
                        (result['bid'] > 0) &
                        (result['assignment_chance'] < 20)
                    ].copy()
                    
                    if not premium_options.empty:
                        best = premium_options.nlargest(1, 'bid').iloc[0]
                        all_options.append((exp_name.split(' ')[0], best))
            
            if all_options:
                best_overall = max(all_options, key=lambda x: x[1]['bid'])
                summary += f"\n🏆 Top Pick: {best_overall[0]} "
                summary += f"${best_overall[1]['strike']:.0f}P ${best_overall[1]['bid']:.2f}"
        else:
            summary += "⚠️ No suitable options found with <20% assignment risk"
        
        return summary
    
    def send_email_sms(self, message):
        """Send SMS via email-to-SMS gateway (free)"""
        try:
            if 'email_sms' not in self.notification_config:
                return False
                
            config = self.notification_config['email_sms']
            
            # Email-to-SMS gateways for major carriers
            carrier_gateways = {
                'verizon': 'vtext.com',
                'att': 'txt.att.net',
                'at&t': 'txt.att.net',
                'tmobile': 'tmomail.net',
                't-mobile': 'tmomail.net',
                'sprint': 'messaging.sprintpcs.com',
                'boost': 'myboostmobile.com',
                'boost mobile': 'myboostmobile.com',
                'cricket': 'sms.cricketwireless.net',
                'cricket wireless': 'sms.cricketwireless.net',
                'uscellular': 'email.uscc.net',
                'us cellular': 'email.uscc.net',
                'metro': 'mymetropcs.com',
                'metropcs': 'mymetropcs.com',
                'metro pcs': 'mymetropcs.com',
                'mint': 'tmomail.net',  # Mint uses T-Mobile network
                'mint mobile': 'tmomail.net'
            }
            
            # Normalize carrier name for better matching
            carrier_normalized = config['carrier'].lower().strip()
            gateway = carrier_gateways.get(carrier_normalized)
            
            if not gateway:
                logging.error(f"Unsupported carrier: {config['carrier']}")
                logging.error(f"Supported carriers: {', '.join(carrier_gateways.keys())}")
                return False
            
            # Create SMS address
            sms_address = f"{config['phone_number']}@{gateway}"
            
            # Send via SMTP
            msg = MIMEText(message)
            msg['From'] = config['from_email']
            msg['To'] = sms_address
            msg['Subject'] = ""  # Empty subject for SMS
            
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(config['from_email'], config['app_password'])
            server.sendmail(config['from_email'], sms_address, msg.as_string())
            server.quit()
            
            logging.info(f"SMS sent successfully via email gateway to {config['phone_number']}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to send SMS via email: {e}")
            return False
    
    def send_webhook_notification(self, message):
        """Send notification via webhook (Discord, Slack, etc.)"""
        try:
            if 'webhook' not in self.notification_config:
                return False
                
            config = self.notification_config['webhook']
            
            if config['type'] == 'discord':
                payload = {
                    "content": message,
                    "username": "Options Analyzer"
                }
            elif config['type'] == 'slack':
                payload = {
                    "text": message,
                    "username": "Options Analyzer"
                }
            else:
                payload = {"message": message}
            
            response = requests.post(
                config['url'], 
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200 or response.status_code == 204:
                logging.info(f"Webhook notification sent successfully")
                return True
            else:
                logging.error(f"Webhook failed with status {response.status_code}")
                return False
                
        except Exception as e:
            logging.error(f"Failed to send webhook notification: {e}")
            return False
    
    def send_pushover_notification(self, message):
        """Send notification via Pushover (free tier available)"""
        try:
            if 'pushover' not in self.notification_config:
                return False
                
            config = self.notification_config['pushover']
            
            payload = {
                'token': config['app_token'],
                'user': config['user_key'],
                'message': message,
                'title': f'{self.ticker_symbol} Options Alert'
            }
            
            response = requests.post(
                'https://api.pushover.net/1/messages.json',
                data=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                logging.info("Pushover notification sent successfully")
                return True
            else:
                logging.error(f"Pushover failed with status {response.status_code}")
                return False
                
        except Exception as e:
            logging.error(f"Failed to send Pushover notification: {e}")
            return False
    
    def send_ntfy_notification(self, message):
        """Send notification via ntfy.sh (completely free)"""
        try:
            if 'ntfy' not in self.notification_config:
                return False
                
            config = self.notification_config['ntfy']
            topic = config['topic']
            
            # ntfy.sh is completely free and doesn't require registration
            url = f"https://ntfy.sh/{topic}"
            
            headers = {
                'Title': f'{self.ticker_symbol} Options Alert',
                'Priority': '3',  # Normal priority
                'Tags': 'money,stocks',
                'Replace': 'options-analysis'  # This will replace previous notifications with same ID
            }
            
            response = requests.post(
                url,
                data=message.encode('utf-8'),
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                logging.info(f"ntfy notification sent successfully to topic: {topic}")
                return True
            else:
                logging.error(f"ntfy failed with status {response.status_code}")
                return False
                
        except Exception as e:
            logging.error(f"Failed to send ntfy notification: {e}")
            return False
    
    def send_notifications(self, results_dict):
        """Send notifications via all configured methods"""
        if not self.notification_config:
            logging.warning("No notification configuration provided")
            return False
        
        # Create messages
        sms_message = self.create_sms_summary(results_dict)
        detailed_message = self.create_detailed_summary(results_dict)
        
        success_count = 0
        
        # Try each configured notification method
        if self.notification_config.get('email_sms', {}).get('enabled', False):
            if self.send_email_sms(sms_message):
                success_count += 1
        
        if self.notification_config.get('webhook', {}).get('enabled', False):
            if self.send_webhook_notification(detailed_message):
                success_count += 1
        
        if self.notification_config.get('pushover', {}).get('enabled', False):
            if self.send_pushover_notification(detailed_message):
                success_count += 1
        
        if self.notification_config.get('ntfy', {}).get('enabled', False):
            if self.send_ntfy_notification(detailed_message):
                success_count += 1
        
        return success_count > 0
    
    def run_automated_analysis(self):
        """Run the full analysis and send notifications"""
        try:
            logging.info(f"Starting automated analysis for {self.ticker_symbol}")
            
            # Run analysis
            success, results = self.run_analysis_multi_expiration()
            
            if not success:
                error_msg = f"Analysis failed for {self.ticker_symbol}: {results}"
                logging.error(error_msg)
                
                # Send error notification
                if self.notification_config:
                    error_sms = f"❌ {self.ticker_symbol} analysis failed"
                    self.send_email_sms(error_sms) if self.notification_config.get('email_sms', {}).get('enabled') else None
                return False
            
            # Send notifications
            if self.notification_config:
                self.send_notifications(results)
            else:
                logging.warning("No notification configuration provided. Analysis completed but not sent.")
                # Print to console instead
                detailed_summary = self.create_detailed_summary(results)
                print(detailed_summary)
            
            logging.info(f"Analysis completed successfully for {self.ticker_symbol}")
            return True
            
        except Exception as e:
            logging.error(f"Error in automated analysis: {e}")
            return False

    def run_single_analysis(self):
        """Run a single analysis without continuous scheduling - for market hours mode"""
        logging.info(f"Starting single analysis for {self.ticker_symbol}")
        return self.run_analysis()


def load_config():
    """Load configuration from config.py"""
    try:
        import config
        return config.NOTIFICATION_CONFIG, config.ANALYSIS_CONFIG, config.NOTIFICATION_SETTINGS
    except ImportError:
        logging.error("Config file not found. Please run setup_sms.py first")
        return None, None, None
    except Exception as e:
        logging.error(f"Error loading config: {e}")
        return None, None, None


def job():
    """Job function that runs every hour"""
    # Load configuration
    notification_config, analysis_config, notification_settings = load_config()
    
    if not notification_config or not analysis_config:
        logging.error("Configuration not loaded. Exiting.")
        return
    
    # Create analyzer and run
    analyzer = AutomatedOptionsAnalyzer(
        ticker_symbol=analysis_config['ticker'],
        price_range_below=analysis_config['price_range'],
        notification_config=notification_config if notification_settings.get('send_notifications', True) else None
    )
    analyzer.run_automated_analysis()


def main():
    """Main function to set up the scheduler"""
    print("🚀 Starting Automated Options Analyzer with SMS")
    print("📱 Will send text notifications every hour")
    print("📋 Check the log file for detailed information")
    print("-" * 50)
    
    # Load configuration
    notification_config, analysis_config, notification_settings = load_config()
    
    if not notification_config or not analysis_config:
        print("❌ Configuration not found. Please run setup_sms.py first")
        print("   python setup_sms.py")
        return
    
    print(f"📊 Analyzing: {analysis_config['ticker']}")
    
    # Show enabled notification methods
    enabled_methods = []
    if notification_config.get('email_sms', {}).get('enabled'):
        phone = notification_config['email_sms']['phone_number']
        enabled_methods.append(f"SMS to {phone}")
    if notification_config.get('webhook', {}).get('enabled'):
        enabled_methods.append(f"Webhook ({notification_config['webhook']['type']})")
    if notification_config.get('pushover', {}).get('enabled'):
        enabled_methods.append("Pushover")
    if notification_config.get('ntfy', {}).get('enabled'):
        enabled_methods.append(f"ntfy.sh/{notification_config['ntfy']['topic']}")
    
    print(f"📱 Notifications: {', '.join(enabled_methods) if enabled_methods else 'None configured'}")
    print(f"⏰ Interval: Every {analysis_config.get('schedule_interval', 'hour')}")
    
    # Schedule based on configuration
    interval = analysis_config.get('schedule_interval', 'hour')
    if interval == 'hour':
        schedule.every().hour.do(job)
    elif interval == '30minutes':
        schedule.every(30).minutes.do(job)
    elif interval == '2hours':
        schedule.every(2).hours.do(job)
    elif interval == 'day':
        schedule.every().day.at("09:00").do(job)  # 9 AM daily
    else:
        schedule.every().hour.do(job)  # Default to hourly
    
    # Run once immediately
    print("🔄 Running initial analysis...")
    job()
    
    # Keep the script running
    print("⏰ Scheduler started. Press Ctrl+C to stop.")
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        print("\n🛑 Scheduler stopped by user")
        logging.info("Automated analyzer stopped by user")


if __name__ == "__main__":
    main()

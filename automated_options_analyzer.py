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
from email.mime.base import MIMEBase
from email import encoders
import io
from contextlib import redirect_stdout
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
    def __init__(self, ticker_symbol="AAPL", price_range_below=30, email_config=None):
        self.ticker_symbol = ticker_symbol.upper()
        self.price_range_below = price_range_below
        self.stock = None
        self.current_price = None
        self.email_config = email_config or {}
        
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
    
    def format_analysis_output(self, results_dict):
        """Format the analysis results as a string for email"""
        output = io.StringIO()
        
        with redirect_stdout(output):
            print(f"{'='*80}")
            print(f"PUT OPTIONS ANALYSIS FOR {self.ticker_symbol}")
            print(f"Current Stock Price: ${self.current_price:.2f}")
            print(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Price Range: ${self.current_price - self.price_range_below:.2f} to ${self.current_price:.2f}")
            print(f"{'='*80}")
            
            # Add explanation for Greeks
            print("\nGREEKS EXPLANATION:")
            print("• Chance of Getting Assigned: Probability (%) of being assigned if held to expiration")
            print("• Daily Decay: Amount ($) the option loses in value each day due to time decay")
            print("-" * 80)
            
            # Display each expiration
            for exp_name, result in results_dict.items():
                if result is not None and not result.empty:
                    print(f"\n{exp_name.upper()}:")
                    print("-" * 50)
                    
                    # Create formatted display with all columns
                    display_data = []
                    for _, row in result.iterrows():
                        assignment_chance = row['assignment_chance'] if 'assignment_chance' in row and pd.notna(row['assignment_chance']) else None
                        daily_decay = row['daily_decay'] if 'daily_decay' in row and pd.notna(row['daily_decay']) else None
                        
                        formatted_row = {
                            'Strike': f"${row['strike']:.2f}",
                            'Bid': f"${row['bid']:.2f}",
                            'Assignment %': f"{assignment_chance:.1f}%" if assignment_chance is not None else "N/A",
                            'Daily Decay': f"${daily_decay:.3f}" if daily_decay is not None else "N/A"
                        }
                        display_data.append(formatted_row)
                    
                    # Convert to DataFrame for nice formatting
                    display_df = pd.DataFrame(display_data)
                    print(display_df.to_string(index=False))
                    
                else:
                    print(f"\n{exp_name.upper()}: No puts found in range")
            
            # Add best options analysis
            self.format_best_options_analysis(results_dict)
        
        return output.getvalue()
    
    def format_best_options_analysis(self, results_dict):
        """Format the best options analysis"""
        print(f"\n{'='*80}")
        print("📈 WEEKLY RECOMMENDATIONS")
        print(f"{'='*80}")
        
        all_premium_options = []
        
        # Collect best option from each week
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
                    
                    # Add to premium analysis
                    premium_data = {
                        'week': exp_name,
                        'strike': best_premium['strike'],
                        'bid': best_premium['bid'],
                        'assignment_chance': best_premium['assignment_chance'],
                        'distance_otm': self.current_price - best_premium['strike'],
                    }
                    all_premium_options.append(premium_data)
        
        if all_premium_options:
            print("\n💰 BEST PREMIUM OPTIONS (<20% Assignment Risk):")
            print("-" * 70)
            for i, option in enumerate(all_premium_options, 1):
                print(f"{i}. {option['week']}")
                print(f"   Strike: ${option['strike']:.2f} (${option['distance_otm']:.0f} OTM)")
                print(f"   Premium: ${option['bid']:.2f}")
                print(f"   Assignment Risk: {option['assignment_chance']:.1f}%")
                print()
            
            # Top recommendation
            highest_premium = max(all_premium_options, key=lambda x: x['bid'])
            safest_premium = min(all_premium_options, key=lambda x: x['assignment_chance'])
            
            print("🎯 TOP RECOMMENDATIONS:")
            print("-" * 30)
            print(f"💪 HIGHEST PREMIUM: ${highest_premium['bid']:.2f} at ${highest_premium['strike']:.2f}")
            print(f"   Week: {highest_premium['week']}")
            print(f"   Risk: {highest_premium['assignment_chance']:.1f}%")
            print()
            print(f"🛡️  SAFEST OPTION: ${safest_premium['bid']:.2f} at ${safest_premium['strike']:.2f}")
            print(f"   Week: {safest_premium['week']}")
            print(f"   Risk: {safest_premium['assignment_chance']:.1f}%")
        
        else:
            print("⚠️  No suitable options found with <20% assignment chance.")
    
    def send_email(self, subject, body, attachment_data=None):
        """Send email with analysis results"""
        try:
            if not self.email_config:
                logging.error("Email configuration not provided")
                return False
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email_config['from_email']
            msg['To'] = self.email_config['to_email']
            msg['Subject'] = subject
            
            # Add body to email
            msg.attach(MIMEText(body, 'plain'))
            
            # Add attachment if provided
            if attachment_data:
                attachment = MIMEText(attachment_data)
                attachment.add_header('Content-Disposition', 'attachment', filename=f"{self.ticker_symbol}_analysis_{datetime.now().strftime('%Y%m%d_%H%M')}.txt")
                msg.attach(attachment)
            
            # Gmail SMTP configuration
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(self.email_config['from_email'], self.email_config['app_password'])
            
            text = msg.as_string()
            server.sendmail(self.email_config['from_email'], self.email_config['to_email'], text)
            server.quit()
            
            logging.info(f"Email sent successfully to {self.email_config['to_email']}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to send email: {e}")
            return False
    
    def run_automated_analysis(self):
        """Run the full analysis and send email"""
        try:
            logging.info(f"Starting automated analysis for {self.ticker_symbol}")
            
            # Run analysis
            success, results = self.run_analysis_multi_expiration()
            
            if not success:
                error_msg = f"Analysis failed for {self.ticker_symbol}: {results}"
                logging.error(error_msg)
                
                # Send error email
                if self.email_config:
                    self.send_email(
                        subject=f"❌ {self.ticker_symbol} Options Analysis Failed",
                        body=error_msg
                    )
                return False
            
            # Format results
            analysis_output = self.format_analysis_output(results)
            
            # Create email subject and body
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            subject = f"📈 {self.ticker_symbol} Options Analysis - {current_time}"
            
            # Create summary for email body
            summary = f"""
Options Analysis Summary for {self.ticker_symbol}
Generated: {current_time}
Current Price: ${self.current_price:.2f}
Price Range Analyzed: ${self.current_price - self.price_range_below:.2f} to ${self.current_price:.2f}

This automated analysis includes:
• 1-4 week put option expirations
• Assignment probability calculations
• Premium optimization recommendations
• Risk assessment for each option

See attached detailed analysis for complete results.

---
Automated Options Analyzer
"""
            
            # Send email
            if self.email_config:
                self.send_email(
                    subject=subject,
                    body=summary,
                    attachment_data=analysis_output
                )
            else:
                logging.warning("No email configuration provided. Analysis completed but not sent.")
                print(analysis_output)  # Print to console instead
            
            logging.info(f"Analysis completed successfully for {self.ticker_symbol}")
            return True
            
        except Exception as e:
            logging.error(f"Error in automated analysis: {e}")
            return False


def load_config():
    """Load configuration from config.py"""
    try:
        import config
        return config.EMAIL_CONFIG, config.ANALYSIS_CONFIG, config.EMAIL_SETTINGS
    except ImportError:
        logging.error("Config file not found. Please run setup_automation.py first")
        return None, None, None
    except Exception as e:
        logging.error(f"Error loading config: {e}")
        return None, None, None


def job():
    """Job function that runs every hour"""
    # Load configuration
    email_config, analysis_config, email_settings = load_config()
    
    if not email_config or not analysis_config:
        logging.error("Configuration not loaded. Exiting.")
        return
    
    # Create analyzer and run
    analyzer = AutomatedOptionsAnalyzer(
        ticker_symbol=analysis_config['ticker'],
        price_range_below=analysis_config['price_range'],
        email_config=email_config if email_settings.get('send_emails', True) else None
    )
    analyzer.run_automated_analysis()


def main():
    """Main function to set up the scheduler"""
    print("🚀 Starting Automated Options Analyzer")
    print("📧 Will run every hour and send email notifications")
    print("📋 Check the log file for detailed information")
    print("-" * 50)
    
    # Load configuration
    email_config, analysis_config, email_settings = load_config()
    
    if not email_config or not analysis_config:
        print("❌ Configuration not found. Please run setup_automation.py first")
        print("   python setup_automation.py")
        return
    
    print(f"📊 Analyzing: {analysis_config['ticker']}")
    print(f"📧 Sending to: {email_config['to_email']}")
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

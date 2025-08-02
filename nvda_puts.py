import yfinance as yf
import pandas as pd
from datetime import datetime
import sys
import numpy as np
from py_vollib.black_scholes.greeks.analytical import delta, theta
from py_vollib.black_scholes import black_scholes
import warnings
warnings.filterwarnings('ignore')

class OptionsAnalyzer:
    def __init__(self, ticker_symbol="AAPL", price_range_below=30):
        self.ticker_symbol = ticker_symbol.upper()
        self.price_range_below = price_range_below
        self.stock = None
        self.current_price = None
        
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
            print(f"Fetching data for {self.ticker_symbol}...")
            self.stock = yf.Ticker(self.ticker_symbol)
            
            # Get current price
            hist = self.stock.history(period="1d")
            if hist.empty:
                raise ValueError(f"No price data available for {self.ticker_symbol}")
            
            self.current_price = hist["Close"].iloc[-1]
            print(f"Current price: ${self.current_price:.2f}")
            return True
            
        except Exception as e:
            print(f"Error fetching stock data: {e}")
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
    
    def get_options_data(self, expiration_index=0):
        """Get options data for specified expiration date"""
        try:
            # Check if options are available
            if not self.stock.options:
                print(f"No options data available for {self.ticker_symbol}")
                return None
            
            print(f"Available expiration dates: {len(self.stock.options)}")
            for i, date in enumerate(self.stock.options[:5]):  # Show first 5
                print(f"  {i}: {date}")
            
            if expiration_index >= len(self.stock.options):
                expiration_index = 0
                print(f"Using nearest expiration date (index 0)")
            
            expiration_date = self.stock.options[expiration_index]
            print(f"Using expiration date: {expiration_date}")
            
            option_chain = self.stock.option_chain(expiration_date)
            return option_chain, expiration_date
            
        except Exception as e:
            print(f"Error fetching options data: {e}")
            return None
    
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
    
    def display_results(self, results_dict):
        """Display formatted results for multiple expirations"""
        if not results_dict:
            print("No data to display.")
            return
        
        print(f"\n{'='*80}")
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
                        'Chance of Getting Assigned': f"{assignment_chance:.1f}%" if assignment_chance is not None else "N/A",
                        'Daily Decay': f"${daily_decay:.3f}" if daily_decay is not None else "N/A"
                    }
                    display_data.append(formatted_row)
                
                # Convert to DataFrame for nice formatting
                display_df = pd.DataFrame(display_data)
                print(display_df.to_string(index=False))
                
            else:
                print(f"\n{exp_name.upper()}: No puts found in range")
    
    def analyze_best_options(self, results_dict):
        """Analyze and recommend the best options based on premium vs assignment risk"""
        print(f"\n{'='*80}")
        print("WEEKLY RECOMMENDATION ANALYSIS")
        print(f"{'='*80}")
        
        # Analyze each week separately
        for exp_name, result in results_dict.items():
            if result is not None and not result.empty:
                print(f"\n📅 {exp_name.upper()}:")
                print("-" * 70)
                
                # Filter for options at least $10 OTM (below current price)
                otm_threshold = self.current_price - 10
                safe_options = result[
                    (result['strike'] <= otm_threshold) & 
                    (pd.notna(result['assignment_chance'])) &
                    (pd.notna(result['bid'])) &
                    (result['bid'] > 0)
                ].copy()
                
                if safe_options.empty:
                    print(f"   ⚠️  No options found at least $10 out-of-the-money")
                    # Still show premium options even if no super safe ones
                else:
                    # Sort by premium-to-risk ratio
                    safe_options = safe_options.sort_values('premium_risk_ratio', ascending=False)
                    
                    # Get top 3 recommendations for this week
                    top_3 = safe_options.head(3)
                    
                    print(f"   🎯 BEST OUT-OF-THE-MONEY OPTIONS (At least ${10:.0f} below ${self.current_price:.2f}):")
                    print(f"   Current Price: ${self.current_price:.2f} | OTM Threshold: ${otm_threshold:.2f}")
                    print()
                    
                    for i, (_, row) in enumerate(top_3.iterrows(), 1):
                        distance_otm = self.current_price - row['strike']
                        print(f"   {i}. STRIKE ${row['strike']:.2f} (${distance_otm:.0f} OTM)")
                        print(f"      Premium: ${row['bid']:.2f}")
                        print(f"      Assignment Chance: {row['assignment_chance']:.1f}%")
                        print(f"      Daily Decay: ${row['daily_decay']:.3f}")
                        print(f"      Premium/Risk Ratio: {row['premium_risk_ratio']:.2f}")
                        print()
                
                # NEW: Add analysis for <20% assignment chance with highest premium
                moderate_risk_options = result[
                    (pd.notna(result['assignment_chance'])) &
                    (pd.notna(result['bid'])) &
                    (result['bid'] > 0) &
                    (result['assignment_chance'] < 20)
                ].copy()
                
                if not moderate_risk_options.empty:
                    # Sort by premium (highest first)
                    best_premium_under_20 = moderate_risk_options.nlargest(3, 'bid')
                    
                    print(f"   💰 BEST PREMIUM WITH <20% ASSIGNMENT RISK:")
                    print(f"   (Maximum income while staying under 20% assignment chance)")
                    print()
                    
                    for i, (_, row) in enumerate(best_premium_under_20.iterrows(), 1):
                        distance_otm = self.current_price - row['strike']
                        print(f"   {i}. STRIKE ${row['strike']:.2f} (${distance_otm:.0f} OTM)")
                        print(f"      Premium: ${row['bid']:.2f}")
                        print(f"      Assignment Chance: {row['assignment_chance']:.1f}%")
                        print(f"      Daily Decay: ${row['daily_decay']:.3f}")
                        print()
                    
                    # Highlight the best premium option under 20%
                    best_premium = best_premium_under_20.iloc[0]
                    distance_otm = self.current_price - best_premium['strike']
                    print(f"   🎯 BEST PREMIUM PICK: Strike ${best_premium['strike']:.2f}")
                    print(f"      → Premium: ${best_premium['bid']:.2f} (${distance_otm:.0f} OTM)")
                    print(f"      → Assignment Risk: {best_premium['assignment_chance']:.1f}%")
                else:
                    print(f"   ⚠️  No options found with <20% assignment chance")
        
        # Overall summary across all weeks
        print(f"\n{'='*80}")
        print("🎯 WEEKLY SUMMARY & STRATEGY RECOMMENDATIONS")
        print(f"{'='*80}")
        
        all_safe_options = []
        all_premium_options = []
        weekly_best = {}
        
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
                        'daily_decay': best_premium['daily_decay'],
                        'premium_risk_ratio': best_premium['premium_risk_ratio'],
                        'distance_otm': self.current_price - best_premium['strike'],
                        'type': 'premium'
                    }
                    all_premium_options.append(premium_data)
        
        if all_premium_options:
            print("\n💰 COMPARISON OF WEEKLY BEST PREMIUM OPTIONS (<20% Assignment):")
            print("-" * 80)
            for i, option in enumerate(all_premium_options, 1):
                print(f"{i}. {option['week']}")
                print(f"   Strike: ${option['strike']:.2f} (${option['distance_otm']:.0f} OTM)")
                print(f"   Premium: ${option['bid']:.2f} | Assignment: {option['assignment_chance']:.1f}%")
                print(f"   Risk Level: {'LOW' if option['assignment_chance'] < 10 else 'MODERATE'}")
                print()
            
            # Strategy recommendations
            print("💡 STRATEGY RECOMMENDATIONS:")
            print("-" * 50)
            
            # Find highest premium under 20%
            highest_premium_safe = max(all_premium_options, key=lambda x: x['bid'])
            print(f"🔥 HIGHEST PREMIUM (<20% RISK): {highest_premium_safe['week']}")
            print(f"   ${highest_premium_safe['bid']:.2f} at ${highest_premium_safe['strike']:.2f} strike")
            print(f"   ({highest_premium_safe['assignment_chance']:.1f}% assignment chance)")
            print()
            
            # Find safest among premium options
            safest_premium = min(all_premium_options, key=lambda x: x['assignment_chance'])
            print(f"🛡️  SAFEST PREMIUM OPTION: {safest_premium['week']}")
            print(f"   ${safest_premium['bid']:.2f} at ${safest_premium['strike']:.2f} strike")
            print(f"   (Only {safest_premium['assignment_chance']:.1f}% assignment chance)")
            print()
            
            # Find balanced option
            balanced_options = [opt for opt in all_premium_options if 5 <= opt['assignment_chance'] <= 15]
            if balanced_options:
                best_balanced = max(balanced_options, key=lambda x: x['bid'])
                print(f"⚖️  BALANCED OPTION (5-15% Risk): {best_balanced['week']}")
                print(f"   ${best_balanced['bid']:.2f} at ${best_balanced['strike']:.2f} strike")
                print(f"   ({best_balanced['assignment_chance']:.1f}% assignment chance)")
                print()
            
            print("🎯 RECOMMENDATIONS BY STRATEGY:")
            print(f"• CONSERVATIVE: Strike ${safest_premium['strike']:.2f} from {safest_premium['week']}")
            print(f"  Premium: ${safest_premium['bid']:.2f} | Risk: {safest_premium['assignment_chance']:.1f}%")
            print(f"• AGGRESSIVE: Strike ${highest_premium_safe['strike']:.2f} from {highest_premium_safe['week']}")
            print(f"  Premium: ${highest_premium_safe['bid']:.2f} | Risk: {highest_premium_safe['assignment_chance']:.1f}%")
            
        else:
            print("⚠️  No suitable options found with <20% assignment chance.")
            print("Consider increasing your risk tolerance or price range.")
        
        return weekly_best
    
    def run_analysis_multi_expiration(self):
        """Run analysis for 1-week, 2-week, 3-week, and 4-week expirations"""
        if not self.fetch_stock_data():
            return False
        
        # Check if options are available
        if not self.stock.options:
            print(f"No options data available for {self.ticker_symbol}")
            return False
        
        print(f"Available expiration dates: {len(self.stock.options)}")
        
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
                    print(f"Error getting {week_label} expiration: {e}")
            else:
                print(f"{week_label} expiration not available (only {len(self.stock.options)} expiration dates)")
        
        self.display_results(results)
        
        # Add analysis of best options
        self.analyze_best_options(results)
        
        return True

def main():
    """Main function with command line argument support"""
    # Default values
    ticker = "AAPL"
    price_range = 30
    
    # Simple command line argument parsing
    if len(sys.argv) > 1:
        ticker = sys.argv[1]
    if len(sys.argv) > 2:
        try:
            price_range = float(sys.argv[2])
        except ValueError:
            print("Invalid price range. Using default: 30")
    
    print(f"Analyzing {ticker} puts within ${price_range} below current price")
    print("Showing 1-week, 2-week, 3-week, and 4-week expirations")
    
    analyzer = OptionsAnalyzer(ticker, price_range)
    success = analyzer.run_analysis_multi_expiration()
    
    if not success:
        print("Analysis failed. Please check the ticker symbol and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()

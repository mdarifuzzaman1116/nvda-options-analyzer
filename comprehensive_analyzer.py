#!/usr/bin/env python3
"""
Multi-Stock Comprehensive Options Analyzer
Analyzes NVDA, AAPL, GOOG, GOOGL with detailed weekly breakdowns
"""

import os
import sys
import pandas as pd
import yfinance as yf
import numpy as np
from datetime import datetime, timedelta
import logging
from py_vollib.black_scholes.greeks.analytical import delta

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class ComprehensiveOptionsAnalyzer:
    def __init__(self):
        # Focus on AAPL only for now
        self.symbols = ['AAPL']
        self.current_prices = {}
        self.risk_free_rate = 0.05  # 5% risk-free rate
        
    def get_stock_data(self, symbol):
        """Get current stock price and options data"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1d")
            current_price = hist['Close'].iloc[-1]
            self.current_prices[symbol] = current_price
            
            logging.info(f"✅ {symbol}: ${current_price:.2f}")
            return ticker, current_price
        except Exception as e:
            logging.error(f"❌ Error fetching {symbol} data: {e}")
            return None, None
    
    def get_option_expiration_dates(self, ticker):
        """Get the next 4 weekly expiration dates"""
        try:
            expirations = ticker.options
            if len(expirations) >= 4:
                return expirations[:4]
            else:
                logging.warning(f"Only {len(expirations)} expiration dates available")
                return expirations
        except Exception as e:
            logging.error(f"Error getting expiration dates: {e}")
            return []
    
    def calculate_strikes_to_analyze(self, current_price):
        """Calculate strikes closer to current price for better opportunities"""
        # Start just $2 below current price for closer strikes
        start_strike = current_price - 2
        # Round down to nearest $1 increment for more granular strikes
        start_strike = int(start_strike)
        
        strikes = []
        # Get strikes $1 apart for first 10, then $2 apart for next 5
        for i in range(15):
            if i < 10:
                strike = start_strike - i  # $1 apart for first 10
            else:
                strike = start_strike - 10 - ((i - 10) * 2)  # $2 apart for remaining
            
            if strike > 0:  # Don't go negative
                strikes.append(strike)
        
        return sorted(strikes, reverse=True)  # Highest to lowest
    
    def calculate_assignment_probability(self, current_price, strike, days_to_expiry, volatility=0.3):
        """Calculate assignment probability using Black-Scholes delta (approximation)"""
        try:
            if days_to_expiry <= 0:
                return 100.0 if current_price <= strike else 0.0
            
            time_to_expiry = days_to_expiry / 365.0
            
            # Calculate delta (proxy for assignment probability)
            delta_value = delta('p', current_price, strike, time_to_expiry, self.risk_free_rate, volatility)
            
            # Convert delta to assignment probability percentage
            assignment_prob = abs(delta_value) * 100
            
            return min(assignment_prob, 100.0)
        except:
            # Fallback calculation if Black-Scholes fails
            distance = ((strike - current_price) / current_price) * 100
            if distance > 0:  # Strike is above current price
                return min(90.0, 5.0 + distance * 2)
            else:  # Strike is below current price
                return max(1.0, 20.0 + distance * 3)
    
    def calculate_premium_risk_ratio(self, premium, assignment_chance):
        """Calculate Premium/Risk Ratio with explanation"""
        if assignment_chance <= 0:
            return float('inf'), "Perfect safety (no assignment risk)"
        
        ratio = (premium * 100) / assignment_chance
        
        if ratio >= 15:
            explanation = "EXCELLENT - High premium per unit of risk"
        elif ratio >= 10:
            explanation = "GOOD - Decent premium for the risk taken"
        elif ratio >= 5:
            explanation = "FAIR - Moderate premium vs risk"
        elif ratio >= 2:
            explanation = "POOR - Low premium for the risk"
        else:
            explanation = "TERRIBLE - Very low premium vs high risk"
            
        return ratio, explanation
    
    def analyze_weekly_options(self, symbol, ticker, current_price, expiration_date, week_num):
        """Analyze options for a specific week"""
        try:
            # Get options chain for this expiration
            options_chain = ticker.option_chain(expiration_date)
            puts = options_chain.puts
            
            if puts.empty:
                return None
            
            # Calculate days to expiry
            exp_date = datetime.strptime(expiration_date, '%Y-%m-%d')
            days_to_expiry = (exp_date - datetime.now()).days
            
            # Get strikes to analyze
            target_strikes = self.calculate_strikes_to_analyze(current_price)
            
            analyzed_options = []
            processed_strikes = set()  # Track which actual strikes we've processed
            
            for strike in target_strikes:
                # Find closest available strike
                available_strikes = puts['strike'].values
                closest_strike = min(available_strikes, key=lambda x: abs(x - strike))
                
                # Skip if we've already processed this actual strike
                if closest_strike in processed_strikes:
                    continue
                    
                processed_strikes.add(closest_strike)
                
                # Get option data for this strike
                option_data = puts[puts['strike'] == closest_strike]
                if option_data.empty:
                    continue
                
                option = option_data.iloc[0]
                premium = (option['bid'] + option['ask']) / 2 if option['bid'] > 0 and option['ask'] > 0 else option['lastPrice']
                
                if premium <= 0:
                    continue
                
                # Calculate metrics
                otm_amount = current_price - closest_strike
                assignment_chance = self.calculate_assignment_probability(current_price, closest_strike, days_to_expiry)
                daily_decay = premium / max(days_to_expiry, 1)
                contract_value = premium * 100  # Value of 1 contract
                
                premium_risk_ratio, ratio_explanation = self.calculate_premium_risk_ratio(premium, assignment_chance)
                
                analyzed_options.append({
                    'strike': closest_strike,
                    'premium': premium,
                    'contract_value': contract_value,
                    'otm_amount': otm_amount,
                    'assignment_chance': assignment_chance,
                    'daily_decay': daily_decay,
                    'premium_risk_ratio': premium_risk_ratio,
                    'ratio_explanation': ratio_explanation,
                    'days_to_expiry': days_to_expiry
                })
            
            return analyzed_options
            
        except Exception as e:
            logging.error(f"Error analyzing {symbol} week {week_num} options: {e}")
            return None
    
    def format_weekly_analysis(self, symbol, current_price, week_num, expiration_date, options_data):
        """Format weekly analysis with clean mobile-friendly format"""
        if not options_data:
            return f"❌ Week {week_num} ({expiration_date}): No data\n\n"
        
        # Sort by strike price and filter good options only
        options_data.sort(key=lambda x: x['strike'], reverse=True)
        good_options = [opt for opt in options_data if opt['premium_risk_ratio'] >= 5]
        
        analysis = f"📅 === WEEK {week_num} - {expiration_date} ===\n"
        analysis += f"💰 Current: ${current_price:.2f}\n\n"
        
        if not good_options:
            analysis += "⚠️  NO PROFITABLE OPTIONS\n\n"
            
        return analysis
    
    def analyze_all_stocks(self):
        """Analyze all stocks and return comprehensive results"""
        all_results = {}
        
        logging.info("🚀 Starting comprehensive multi-stock analysis...")
        
        for symbol in self.symbols:
            logging.info(f"📊 Analyzing {symbol}...")
            ticker, current_price = self.get_stock_data(symbol)
            
            if not ticker or not current_price:
                continue
            
            # Get expiration dates
            expirations = self.get_option_expiration_dates(ticker)
            if not expirations:
                continue
            
            stock_results = {
                'current_price': current_price,
                'weekly_analysis': {}
            }
            
            # Analyze each week
            for i, exp_date in enumerate(expirations[:4], 1):
                week_options = self.analyze_weekly_options(symbol, ticker, current_price, exp_date, i)
                if week_options:
                    stock_results['weekly_analysis'][i] = {
                        'expiration_date': exp_date,
                        'options': week_options
                    }
            
            all_results[symbol] = stock_results
        
        return all_results
    
    def create_comprehensive_report(self, all_results):
        """Create the comprehensive notification report with detailed weekly analysis"""
        # Get AAPL current price for the header
        current_price = all_results.get('AAPL', {}).get('current_price', 0)
        
        report = f"🚀 OPTIONS ALERT - AAPL (${current_price:.2f}) 🚀\n"
        report += f"⏰ Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M EST')}\n"
        report += f"📊 Analyzing: AAPL Put Options\n"
        report += f"💰 Potential Profit × 100 for actual contract values\n"
        report += f"🎯 Strikes within $15 of current price\n\n"
        
        # Track best picks for each stock and week
        weekly_bests = {}  # {week: [(symbol, premium, details), ...]}
        stock_summaries = {}  # {symbol: best_overall}
        
        # First pass: collect all weekly best picks
        for week_num in range(1, 5):
            weekly_bests[week_num] = []
            
            for symbol, data in all_results.items():
                if 'weekly_analysis' not in data or week_num not in data['weekly_analysis']:
                    continue
                    
                week_data = data['weekly_analysis'][week_num]
                options = week_data['options']
                
                # Find best pick for this week
                under_20_risk = [opt for opt in options if opt['assignment_chance'] < 20]
                if under_20_risk:
                    best = max(under_20_risk, key=lambda x: x['premium'])
                    best['expiration_date'] = week_data['expiration_date']  # Add expiration date
                    weekly_bests[week_num].append((symbol, best['premium'], best))
                    
                    # Track best for each stock overall
                    if symbol not in stock_summaries or best['premium'] > stock_summaries[symbol]['premium']:
                        stock_summaries[symbol] = {
                            'week': week_num,
                            'premium': best['premium'],
                            'details': best,
                            'expiration_date': week_data['expiration_date']
                        }
        
        # ABSOLUTE BEST CHOICE at the very top
        if stock_summaries:
            best_symbol = 'AAPL'  # Only AAPL now
            if best_symbol in stock_summaries:
                best_data = stock_summaries[best_symbol]
                details = best_data['details']
                
                report += "⭐ === ABSOLUTE BEST CHOICE === ⭐\n"
                report += f"🥇 {best_symbol} Week {best_data['week']}\n"
                report += f"📅 Expiration: {best_data['expiration_date']}\n"
                report += f"💰 Potential profit: ${best_data['premium']:.2f} per share that would be ${details['contract_value']:.0f}\n"
                report += f"🎯 Strike: ${details['strike']:.0f}\n"
                report += f"💵 Contract Value: ${details['contract_value']:.0f}\n"
                report += f"⚠️ Assignment Risk: {details['assignment_chance']:.1f}%\n"
                report += f"⏰ Daily Time Decay: ${details['daily_decay']:.3f}\n"
                report += f"🚀 Total Profit Potential: ${details['contract_value']:.0f} per contract\n\n"
        
        # WEEKLY BEST PICKS SUMMARY - Sorted by Quality (Excellent > Good > Fair)
        report += "🏆 === WEEKLY BEST PICKS SUMMARY === 🏆\n\n"
        
        # Collect all weekly picks with quality scores for sorting
        all_weekly_picks = []
        for week_num in range(1, 5):
            if week_num in weekly_bests and weekly_bests[week_num]:
                # Sort by premium (highest first)
                week_picks = sorted(weekly_bests[week_num], key=lambda x: x[1], reverse=True)
                best_symbol, best_premium, best_details = week_picks[0]
                
                # Determine quality score for sorting (higher is better)
                if best_details['premium_risk_ratio'] >= 15:
                    quality_score = 3
                    color_emoji = "🟢"
                    quality = "EXCELLENT"
                elif best_details['premium_risk_ratio'] >= 10:
                    quality_score = 2
                    color_emoji = "🟡"
                    quality = "GOOD"
                elif best_details['premium_risk_ratio'] >= 5:
                    quality_score = 1
                    color_emoji = "�"
                    quality = "FAIR"
                else:
                    quality_score = 0
                    color_emoji = "🔴"
                    quality = "RISKY"
                
                all_weekly_picks.append((quality_score, week_num, best_symbol, best_premium, best_details, color_emoji, quality))
        
        # Sort by quality (Excellent > Good > Fair), then by premium
        all_weekly_picks.sort(key=lambda x: (x[0], x[3]), reverse=True)
        
        # Display sorted weekly picks
        for quality_score, week_num, best_symbol, best_premium, best_details, color_emoji, quality in all_weekly_picks:
            report += f"{color_emoji} WEEK {week_num} BEST: {best_symbol}\n"
            report += f"   📅 Expiration: {best_details['expiration_date']}\n"
            report += f"   💰 Potential Profit: ${best_premium:.2f} or ${best_details['contract_value']:.0f}\n"
            report += f"   🎯 Strike: ${best_details['strike']:.0f}\n"
            report += f"   ⚠️  Assignment Risk: {best_details['assignment_chance']:.1f}%\n"
            report += f"   ⏰ Daily Time Decay: ${best_details['daily_decay']:.3f}\n"
            report += f"   {color_emoji} Quality: {quality}\n\n"
        
        report += "=" * 60 + "\n\n"
        
        # DETAILED ANALYSIS SECTION: Show detailed breakdown for each week
        report += "📊 === DETAILED WEEKLY ANALYSIS === 📊\n\n"
        
        # Show detailed analysis for each week
        for week_num in range(1, 5):
            report += f"🗓️ === WEEK {week_num} DETAILED ANALYSIS ===\n\n"
            
            # Show detailed analysis for AAPL for this week
            for symbol, data in all_results.items():
                if 'weekly_analysis' not in data or week_num not in data['weekly_analysis']:
                    continue
                    
                current_price = data['current_price']
                week_data = data['weekly_analysis'][week_num]
                expiration_date = week_data['expiration_date']
                options = week_data['options']
                
                # Generate detailed weekly analysis for this stock
                weekly_report = self.format_weekly_analysis(
                    symbol, current_price, week_num, expiration_date, options
                )
                report += weekly_report
            
            report += "=" * 50 + "\n\n"
        
        return report

def main():
    """Main function for comprehensive analysis"""
    logging.basicConfig(level=logging.INFO)
    
    analyzer = ComprehensiveOptionsAnalyzer()
    results = analyzer.analyze_all_stocks()
    
    if results:
        comprehensive_report = analyzer.create_comprehensive_report(results)
        print(comprehensive_report)
        return comprehensive_report
    else:
        print("❌ No results to display")
        return None

if __name__ == "__main__":
    main()

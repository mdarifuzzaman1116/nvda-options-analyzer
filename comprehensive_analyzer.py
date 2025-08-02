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
        # Multiple stock symbols to analyze
        self.symbols = ['NVDA', 'AAPL', 'GOOG', 'GOOGL']
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
        """Calculate 10 strikes starting $10 below current price"""
        start_strike = current_price - 10
        # Round down to nearest $5 increment for cleaner strikes
        start_strike = int(start_strike / 5) * 5
        
        strikes = []
        for i in range(10):
            strike = start_strike - (i * 5)  # Every $5 below
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
            
            # Get strikes to analyze (10 strikes starting $10 below current price)
            target_strikes = self.calculate_strikes_to_analyze(current_price)
            
            analyzed_options = []
            
            for strike in target_strikes:
                # Find closest available strike
                available_strikes = puts['strike'].values
                closest_strike = min(available_strikes, key=lambda x: abs(x - strike))
                
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
        """Format weekly analysis for one stock"""
        if not options_data:
            return f"📅 {week_num}-WEEK EXPIRATION ({expiration_date}):\n❌ No options data available\n\n"
        
        # Sort by different criteria
        otm_threshold = current_price - 10
        otm_options = [opt for opt in options_data if opt['otm_amount'] >= 10]
        under_20_risk = [opt for opt in options_data if opt['assignment_chance'] < 20]
        
        # Sort OTM options by premium/risk ratio
        otm_options.sort(key=lambda x: x['premium_risk_ratio'], reverse=True)
        
        # Sort under 20% risk by premium
        under_20_risk.sort(key=lambda x: x['premium'], reverse=True)
        
        analysis = f"📅 {week_num}-WEEK EXPIRATION ({expiration_date}):\n"
        analysis += "----------------------------------------------------------------------\n"
        analysis += f"   🎯 BEST OUT-OF-THE-MONEY OPTIONS (At least $10 below ${current_price:.2f}):\n"
        analysis += f"   Current Price: ${current_price:.2f} | OTM Threshold: ${otm_threshold:.2f}\n\n"
        
        # Show top 3 OTM options
        for i, opt in enumerate(otm_options[:3], 1):
            analysis += f"   {i}. STRIKE ${opt['strike']:.2f} (${opt['otm_amount']:.0f} OTM)\n"
            analysis += f"      Premium: ${opt['premium']:.2f} (${opt['contract_value']:.0f} per contract)\n"
            analysis += f"      Assignment Chance: {opt['assignment_chance']:.1f}%\n"
            analysis += f"      Daily Decay: ${opt['daily_decay']:.3f}\n"
            analysis += f"      Premium/Risk Ratio: {opt['premium_risk_ratio']:.2f} - {opt['ratio_explanation']}\n\n"
        
        analysis += "   💰 BEST PREMIUM WITH <20% ASSIGNMENT RISK:\n"
        analysis += "   (Maximum income while staying under 20% assignment chance)\n\n"
        
        # Show top 3 under 20% risk
        for i, opt in enumerate(under_20_risk[:3], 1):
            analysis += f"   {i}. STRIKE ${opt['strike']:.2f} (${opt['otm_amount']:.0f} OTM)\n"
            analysis += f"      Premium: ${opt['premium']:.2f} (${opt['contract_value']:.0f} per contract)\n"
            analysis += f"      Assignment Chance: {opt['assignment_chance']:.1f}%\n"
            analysis += f"      Daily Decay: ${opt['daily_decay']:.3f}\n"
            analysis += f"      Premium/Risk Ratio: {opt['premium_risk_ratio']:.2f} - {opt['ratio_explanation']}\n\n"
        
        # Best pick for this week
        if under_20_risk:
            best_pick = under_20_risk[0]
            analysis += f"   🎯 BEST PREMIUM PICK: Strike ${best_pick['strike']:.2f}\n"
            analysis += f"      → Premium: ${best_pick['premium']:.2f} (${best_pick['otm_amount']:.0f} OTM)\n"
            analysis += f"      → Contract Value: ${best_pick['contract_value']:.0f}\n"
            analysis += f"      → Assignment Risk: {best_pick['assignment_chance']:.1f}%\n\n"
        
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
        """Create the comprehensive notification report"""
        report = "=" * 80 + "\n"
        report += "COMPREHENSIVE WEEKLY OPTIONS ANALYSIS\n"
        report += "=" * 80 + "\n\n"
        
        # Track best picks across all stocks for final recommendations
        all_best_picks = []
        
        # Analyze each stock
        for symbol, data in all_results.items():
            if 'weekly_analysis' not in data:
                continue
                
            report += f"🏢 {symbol} ANALYSIS\n"
            report += "=" * 50 + "\n\n"
            
            current_price = data['current_price']
            
            # Generate weekly analysis for this stock
            for week_num in range(1, 5):
                if week_num in data['weekly_analysis']:
                    week_data = data['weekly_analysis'][week_num]
                    expiration_date = week_data['expiration_date']
                    options = week_data['options']
                    
                    weekly_report = self.format_weekly_analysis(
                        symbol, current_price, week_num, expiration_date, options
                    )
                    report += weekly_report
                    
                    # Track best pick for final recommendations
                    under_20_risk = [opt for opt in options if opt['assignment_chance'] < 20]
                    if under_20_risk:
                        best = max(under_20_risk, key=lambda x: x['premium'])
                        all_best_picks.append({
                            'symbol': symbol,
                            'week': week_num,
                            'expiration': expiration_date,
                            'strike': best['strike'],
                            'premium': best['premium'],
                            'contract_value': best['contract_value'],
                            'assignment_chance': best['assignment_chance'],
                            'premium_risk_ratio': best['premium_risk_ratio']
                        })
            
            report += "\n"
        
        # Final recommendations
        report += "=" * 80 + "\n"
        report += "🎯 CROSS-STOCK SUMMARY & TOP RECOMMENDATIONS\n"
        report += "=" * 80 + "\n\n"
        
        if all_best_picks:
            # Sort by premium (highest first)
            all_best_picks.sort(key=lambda x: x['premium'], reverse=True)
            
            report += "💰 TOP 2 HIGHEST PREMIUM RECOMMENDATIONS (<20% Assignment Risk):\n"
            report += "-" * 70 + "\n"
            
            for i, pick in enumerate(all_best_picks[:2], 1):
                report += f"🏆 #{i} RECOMMENDATION: {pick['symbol']}\n"
                report += f"   Week: {pick['week']}-Week Expiration ({pick['expiration']})\n"
                report += f"   Strike: ${pick['strike']:.2f}\n"
                report += f"   Premium: ${pick['premium']:.2f} (${pick['contract_value']:.0f} per contract)\n"
                report += f"   Assignment Risk: {pick['assignment_chance']:.1f}%\n"
                report += f"   Premium/Risk Ratio: {pick['premium_risk_ratio']:.2f}\n"
                report += f"   🎯 Why This Pick: High premium with manageable risk\n\n"
            
            # Show all stocks summary
            report += "📊 ALL STOCKS BEST WEEKLY PICKS COMPARISON:\n"
            report += "-" * 50 + "\n"
            
            stock_bests = {}
            for pick in all_best_picks:
                if pick['symbol'] not in stock_bests:
                    stock_bests[pick['symbol']] = pick
            
            for symbol, pick in stock_bests.items():
                report += f"{symbol}: ${pick['premium']:.2f} premium, {pick['assignment_chance']:.1f}% risk\n"
        
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

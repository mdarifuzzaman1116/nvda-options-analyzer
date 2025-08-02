#!/bin/bash
# GitHub Codespaces Market Hours Analyzer

echo "🏦 Starting Market Hours NVDA Options Analyzer for Codespaces"
echo "📅 Will run Monday-Friday, 9 AM - 4 PM EST only"
echo "⏰ Analyzes every hour during market hours"
echo "💰 Optimized for 60 free hours/month"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "🚀 Starting market hours analyzer..."
echo "📱 Make sure you have ntfy app installed and subscribed to 'options_price'"
echo ""

# Start the market hours analyzer
python market_hours_analyzer.py

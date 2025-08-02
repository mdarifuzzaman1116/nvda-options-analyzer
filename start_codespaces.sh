#!/bin/bash
# GitHub Codespaces Efficient Options Analyzer

echo "⚡ Starting Efficient NVDA Options Analyzer for Codespaces"
echo "⏰ Runs 2 minutes every hour then stops (14 min/day total)"
echo "💰 97% resource savings vs continuous running"
echo "📊 Monthly usage: ~7 hours (vs 210 hours continuous)"
echo "🧪 Testing mode enabled for weekend testing"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "🚀 Starting efficient analyzer..."
echo "📱 Make sure you have ntfy app installed and subscribed to 'options_price'"
echo "⏱️ Each analysis runs for max 2 minutes then sleeps until next hour"
echo ""

# Start the efficient analyzer
python efficient_analyzer.py

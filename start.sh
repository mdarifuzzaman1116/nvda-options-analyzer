#!/bin/bash
# Render.com startup script
echo "🚀 Starting NVDA Options Analyzer on Render..."

# Install dependencies
pip install --no-cache-dir -r requirements.txt

# Start the application
python cloud_main.py

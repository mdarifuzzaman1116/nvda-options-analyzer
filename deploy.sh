#!/bin/bash
# Quick deployment script for Railway.app

echo "🚀 Setting up for cloud deployment..."

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📦 Initializing git repository..."
    git init
    git add .
    git commit -m "Initial commit - NVDA Options Analyzer"
fi

echo "✅ Ready for deployment!"
echo ""
echo "Next steps:"
echo "1. Push to GitHub:"
echo "   git remote add origin YOUR_GITHUB_REPO_URL"
echo "   git push -u origin main"
echo ""
echo "2. Deploy to Railway.app:"
echo "   - Go to railway.app"
echo "   - Sign up with GitHub"
echo "   - Create new project from GitHub repo"
echo "   - Railway will auto-deploy!"
echo ""
echo "3. Get notifications:"
echo "   - Install ntfy app on phone"
echo "   - Subscribe to topic: options_price"
echo "   - Done! You'll get hourly NVDA analysis"

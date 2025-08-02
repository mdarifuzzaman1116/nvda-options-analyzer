# 🚀 Deploying to Render.com - Step by Step

## Prerequisites ✅
- [x] Signed up for Render.com account
- [x] Have this code ready to deploy

## Step 1: Push Code to GitHub

First, let's get your code on GitHub:

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "NVDA Options Analyzer - Ready for Render deployment"

# Create GitHub repo and push
# Go to github.com, create new repository, then:
git remote add origin YOUR_GITHUB_REPO_URL
git push -u origin main
```

## Step 2: Deploy on Render

1. **Go to Render Dashboard**
   - Visit [dashboard.render.com](https://dashboard.render.com)
   - Click "New +" button

2. **Create Background Worker**
   - Select "Background Worker" (not Web Service)
   - This is perfect for scripts that run continuously

3. **Connect GitHub**
   - Choose "Build and deploy from a Git repository"
   - Connect your GitHub account
   - Select your repository

4. **Configure Service**
   ```
   Name: nvda-options-analyzer
   Environment: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: python cloud_main.py
   ```

5. **Deploy**
   - Click "Create Background Worker"
   - Render will automatically build and deploy

## Step 3: Verify It's Working

**Check Logs:**
- In Render dashboard, click on your service
- Go to "Logs" tab
- You should see: "🚀 Starting cloud-based options analyzer..."

**Check Notifications:**
- Make sure ntfy app is installed on your phone
- Subscribed to topic: `options_price`
- You should get NVDA analysis within an hour

## Step 4: Monitor

**Render Dashboard:**
- Shows if service is running
- View real-time logs
- Monitor resource usage

**Phone Notifications:**
- Hourly NVDA options analysis
- Auto-clearing notifications (only latest shown)

## 💰 Cost Breakdown

- **Render.com**: 750 hours/month FREE (24/7 = 744 hours)
- **ntfy.sh**: Completely FREE
- **Total**: $0/month for normal usage

## 🔧 Troubleshooting

**If deployment fails:**
1. Check Render logs for errors
2. Verify requirements.txt is correct
3. Ensure cloud_main.py exists

**If no notifications:**
1. Check Render logs show "ntfy notification sent"
2. Verify phone has ntfy app installed
3. Confirm subscribed to correct topic: `options_price`

**Service goes to sleep:**
- Free tier may sleep after 15 minutes of inactivity
- Your script keeps it awake by running every hour
- Upgrade to paid tier ($7/month) for guaranteed always-on

## 🎉 Success!

Once deployed, your NVDA options analyzer will:
- ✅ Run 24/7 in the cloud
- ✅ Analyze options every hour
- ✅ Send notifications to your phone
- ✅ Auto-restart if it crashes
- ✅ Cost $0/month on free tier

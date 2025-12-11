# 🚀 Render Deployment Guide - AI Grading System

**Quick guide to deploy the AI-Powered Grading System to Render.com**

---

## 📋 Prerequisites

Before deploying, ensure you have:

- ✅ GitHub account with this repository
- ✅ Render account (sign up at https://render.com)
- ✅ MongoDB Atlas account (free tier: https://www.mongodb.com/cloud/atlas)
- ✅ OpenAI API key (get at https://platform.openai.com)

---

## 🚀 Quick Deploy (5 Minutes)

### Step 1: Prepare MongoDB Atlas

1. **Create MongoDB Atlas Account**
   - Go to https://www.mongodb.com/cloud/atlas
   - Sign up for free tier

2. **Create a Cluster**
   - Click "Build a Cluster"
   - Choose "Free Tier" (M0)
   - Select your region
   - Click "Create Cluster"

3. **Create Database User**
   - Go to "Database Access"
   - Add new database user
   - Username: `admin`
   - Password: Generate secure password
   - Save credentials!

4. **Configure Network Access**
   - Go to "Network Access"
   - Click "Add IP Address"
   - Select "Allow Access from Anywhere" (0.0.0.0/0)
   - Confirm

5. **Get Connection String**
   - Click "Connect" on your cluster
   - Choose "Connect your application"
   - Copy the connection string:
     ```
     mongodb+srv://admin:<password>@cluster0.xxxxx.mongodb.net/ai_grading?retryWrites=true&w=majority
     ```
   - Replace `<password>` with your actual password

---

### Step 2: Deploy to Render

1. **Sign in to Render**
   - Go to https://dashboard.render.com
   - Sign in with GitHub

2. **Create New Web Service**
   - Click "New +" button
   - Select "Web Service"
   - Connect your GitHub repository

3. **Configure Service**
   ```
   Name: ai-grading-system
   Region: Choose closest to you
   Branch: main
   Root Directory: (leave blank)
   Environment: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: gunicorn app:app --bind 0.0.0.0:$PORT
   ```

4. **Select Plan**
   - Choose "Free" for testing
   - Or "Starter" ($7/month) for production

---

### Step 3: Configure Environment Variables

Add these environment variables in Render dashboard:

#### Required Variables:

```env
FLASK_ENV=production
SECRET_KEY=your-super-secret-key-change-this-to-something-random
MONGODB_URI=mongodb+srv://admin:password@cluster0.xxxxx.mongodb.net/ai_grading
OPENAI_API_KEY=sk-your-openai-api-key-here
PORT=10000
```

#### Optional Variables (Recommended):

```env
REDIS_URL=redis://red-xxxxx:6379
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-specific-password
SENTRY_DSN=https://your-sentry-dsn
JWT_SECRET_KEY=another-random-secret-key
```

#### How to Add Variables:
1. In your web service, go to "Environment" tab
2. Click "Add Environment Variable"
3. Enter key and value
4. Click "Save Changes"

---

### Step 4: Deploy

1. **Trigger Deploy**
   - Render will automatically start building
   - Watch the logs in real-time
   - Build takes 2-5 minutes

2. **Wait for Success**
   - Look for "Your service is live 🎉"
   - Note your URL: `https://ai-grading-system.onrender.com`

3. **Verify Deployment**
   - Visit: `https://your-app.onrender.com`
   - Check health: `https://your-app.onrender.com/health`
   - Should return: `{"status": "healthy"}`

---

## 🔐 Generating Secret Keys

### SECRET_KEY (Python)
```python
import secrets
print(secrets.token_hex(32))
```

### Or use online generator:
- https://www.lastpass.com/features/password-generator
- Generate 64-character password

### JWT_SECRET_KEY
Same as SECRET_KEY, but different value.

---

## 📧 Email Configuration (Gmail)

If you want email notifications:

1. **Enable 2-Step Verification** in Google Account
2. **Generate App Password**:
   - Go to: https://myaccount.google.com/apppasswords
   - Select "Mail" and "Other (Custom name)"
   - Name it "AI Grading System"
   - Copy the 16-character password
   
3. **Add to Environment Variables**:
   ```env
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USERNAME=your.email@gmail.com
   MAIL_PASSWORD=xxxx xxxx xxxx xxxx
   ```

---

## 🔴 Redis Setup (Optional)

For better caching and performance:

1. **In Render Dashboard**
   - Click "New +" → "Redis"
   - Name: `ai-grading-redis`
   - Plan: Free tier
   - Click "Create Redis"

2. **Copy Internal Redis URL**
   - Format: `redis://red-xxxxx:6379`

3. **Add to Web Service Environment**
   ```env
   REDIS_URL=redis://red-xxxxx:6379
   ```

---

## 🎯 Post-Deployment Checklist

After deployment, verify:

- [ ] ✅ App loads at your Render URL
- [ ] ✅ Health check responds: `/health`
- [ ] ✅ Can access login page: `/login`
- [ ] ✅ MongoDB connection working (check logs)
- [ ] ✅ Can create account and login
- [ ] ✅ Can submit test assignment
- [ ] ✅ AI grading works (if OPENAI_API_KEY set)
- [ ] ✅ Email notifications work (if configured)

---

## 📊 Monitoring Your Deployment

### View Logs
1. Go to your service in Render
2. Click "Logs" tab
3. Watch real-time logs
4. Look for errors or warnings

### Check Metrics
1. Click "Metrics" tab
2. View:
   - CPU usage
   - Memory usage
   - Request count
   - Response time

### Health Checks
Render automatically monitors: `https://your-app.onrender.com/health`

---

## 🐛 Troubleshooting

### Issue: Build Fails

**Check:**
- Requirements.txt is correct
- Python version compatible
- Build command is correct: `pip install -r requirements.txt`

**Solution:**
```bash
Build Command: pip install --upgrade pip && pip install -r requirements.txt
```

### Issue: App Crashes on Start

**Check Logs for:**
- Missing environment variables
- MongoDB connection errors
- Port binding issues

**Verify:**
```env
PORT=10000
MONGODB_URI is correct (with password)
SECRET_KEY is set
```

### Issue: MongoDB Connection Timeout

**Fix:**
1. Check MongoDB Atlas Network Access
2. Ensure "Allow from Anywhere" (0.0.0.0/0)
3. Verify connection string has correct password
4. Check cluster is running

### Issue: 502 Bad Gateway

**Reasons:**
- App not binding to correct port
- Crash during startup
- Dependency issues

**Fix:**
```bash
Start Command: gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120
```

### Issue: OpenAI API Not Working

**Check:**
- API key is valid: `sk-...`
- API key has credits
- Environment variable name: `OPENAI_API_KEY`

---

## ⚙️ Advanced Configuration

### Custom Domain

1. Go to "Settings" in your web service
2. Scroll to "Custom Domain"
3. Click "Add Custom Domain"
4. Follow DNS configuration instructions

### Auto-Deploy from GitHub

1. Go to "Settings"
2. Find "Auto-Deploy"
3. Toggle ON
4. Now every push to main triggers deploy

### Environment Variables from File

Can't use `.env` file on Render. Must set each variable individually in dashboard.

### Scaling

**Free Tier Limitations:**
- 512 MB RAM
- 0.1 CPU
- Spins down after 15 min inactivity
- 750 hours/month

**Starter Plan ($7/month):**
- 512 MB RAM
- 0.5 CPU
- Always on
- No spin down

**To Upgrade:**
1. Go to your service
2. Click "Settings"
3. Change "Instance Type"
4. Confirm

---

## 🔒 Security Best Practices

1. **Never commit secrets to Git**
   - Use Render's environment variables
   - Add `.env` to `.gitignore`

2. **Use Strong Secret Keys**
   - At least 32 characters
   - Random and unique
   - Different for each environment

3. **Limit MongoDB Access**
   - Use strong passwords
   - Restrict IP when possible
   - Use separate user per app

4. **Enable HTTPS**
   - Render provides free SSL
   - Always use `https://` URLs
   - Set `SESSION_COOKIE_SECURE=True`

5. **Monitor Logs**
   - Check for suspicious activity
   - Watch for failed login attempts
   - Monitor API usage

---

## 💰 Cost Estimation

### Free Tier (For Testing)
```
Web Service:    Free (750 hrs/month)
MongoDB Atlas:  Free (M0 cluster)
Redis:          Free (25 MB)
Total:          $0/month
```

### Starter Setup (Production)
```
Web Service:    $7/month (always on)
MongoDB Atlas:  Free (M0) or $9/month (M2)
Redis:          Free or $5/month
Total:          $7-21/month
```

### Professional Setup
```
Web Service:    $25/month (2GB RAM)
MongoDB Atlas:  $25/month (M10 cluster)
Redis:          $10/month (1GB)
Total:          $60/month
```

---

## 📚 Additional Resources

- **Render Documentation:** https://render.com/docs
- **MongoDB Atlas Docs:** https://docs.atlas.mongodb.com
- **OpenAI API Docs:** https://platform.openai.com/docs
- **Flask Deployment:** https://flask.palletsprojects.com/en/2.3.x/deploying/

---

## 🎯 Quick Command Reference

### View Logs
```bash
# In Render dashboard, click "Logs" or use CLI:
render logs -f
```

### Restart Service
```bash
# In dashboard: "Manual Deploy" → "Clear build cache & deploy"
```

### Check Health
```bash
curl https://your-app.onrender.com/health
```

### Test API
```bash
curl https://your-app.onrender.com/api/health
```

---

## 🚀 Success!

If everything is working:

✅ Your app is live at: `https://your-app.onrender.com`
✅ MongoDB is connected
✅ OpenAI API is working
✅ Users can register and login
✅ Assignments can be submitted and graded

**Congratulations! Your AI Grading System is deployed! 🎉**

---

## 📞 Need Help?

- **Render Support:** support@render.com
- **Project Issues:** GitHub Issues
- **Documentation:** See all .md files in project

---

**Last Updated:** December 11, 2024  
**Version:** 2.0.0  
**Status:** Production Ready ✅
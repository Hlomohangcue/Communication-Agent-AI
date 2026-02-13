# Pre-Deployment Checklist

Before deploying to Vultr, make sure you have everything ready!

---

## ✅ Required Items

### 1. Vultr Account
- [ ] Created account at https://www.vultr.com
- [ ] Added payment method
- [ ] Have at least $6 credit (for 1 month of smallest VM)

### 2. Google Gemini API Key
- [ ] Obtained API key from https://makersuite.google.com/app/apikey
- [ ] Tested API key works (optional but recommended)
- [ ] Saved API key in secure location

### 3. Project Files
- [ ] All project files are ready
- [ ] `.env.example` file exists
- [ ] `requirements.txt` is up to date
- [ ] Frontend files are in `frontend/` directory
- [ ] Backend files are in `backend/` directory

### 4. Code Repository (Recommended)
- [ ] Code pushed to GitHub/GitLab/Bitbucket
- [ ] Repository is accessible (public or have access token)
- [ ] All recent changes are committed

### 5. Local Testing
- [ ] Backend runs locally without errors
- [ ] Frontend connects to backend successfully
- [ ] Can create account and login
- [ ] Can send messages and get AI responses
- [ ] All emoji gestures work correctly

---

## 📋 Pre-Deployment Tasks

### Update Configuration Files

#### 1. Check requirements.txt
```bash
# Make sure all dependencies are listed
cat requirements.txt
```

Should include:
- fastapi
- uvicorn
- google-generativeai
- pydantic
- bcrypt
- PyJWT
- python-multipart
- requests

#### 2. Verify .env.example
```bash
# Make sure example file exists
cat .env.example
```

Should contain:
```
GEMINI_API_KEY=your-api-key-here
```

#### 3. Test Backend Locally
```bash
cd backend
python main.py
```

Should show:
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

#### 4. Test Frontend Locally
Open `frontend/login.html` in browser and verify:
- [ ] Page loads without errors
- [ ] Can create account
- [ ] Can login
- [ ] Dashboard loads
- [ ] Can start simulation
- [ ] Can send messages

---

## 🔍 Code Review Checklist

### Security
- [ ] No hardcoded API keys in code
- [ ] `.env` file is in `.gitignore`
- [ ] Passwords are hashed (using bcrypt)
- [ ] JWT tokens are used for authentication
- [ ] No sensitive data in frontend code

### Configuration
- [ ] `API_BASE` in `frontend/app.js` is set to `http://localhost:8000` (will be updated during deployment)
- [ ] Database path is correct in `backend/database/db.py`
- [ ] CORS settings allow frontend domain

### Files to Check
```bash
# Check .gitignore includes:
cat .gitignore
```

Should include:
```
.env
*.db
*.db-journal
__pycache__/
*.pyc
.DS_Store
node_modules/
```

---

## 📦 Prepare Deployment Package

### Option 1: GitHub Repository (Recommended)

```bash
# Make sure everything is committed
git status

# Add any new files
git add .

# Commit changes
git commit -m "Prepare for deployment"

# Push to GitHub
git push origin main

# Note your repository URL
# Example: https://github.com/yourusername/communication-bridge-ai.git
```

### Option 2: Manual Upload

```bash
# Create deployment package
tar -czf deployment.tar.gz \
  backend/ \
  frontend/ \
  requirements.txt \
  .env.example \
  README.md

# Verify package
tar -tzf deployment.tar.gz | head -20
```

---

## 💰 Cost Estimation

### Vultr VM Costs

| Plan | vCPU | RAM | Storage | Bandwidth | Price/Month |
|------|------|-----|---------|-----------|-------------|
| Basic | 1 | 1GB | 25GB SSD | 1TB | $6 |
| Standard | 1 | 2GB | 55GB SSD | 2TB | $12 |
| Performance | 2 | 4GB | 80GB SSD | 3TB | $24 |

**Recommended for:**
- Development/Testing: $6/month plan
- Small Production: $12/month plan
- Production: $24/month plan

### Additional Costs (Optional)
- Auto Backups: +$1.20/month (20% of server cost)
- Domain Name: ~$10-15/year (from domain registrar)
- SSL Certificate: Free (Let's Encrypt)

### Total Estimated Cost
- **Minimum**: $6/month (VM only)
- **Recommended**: $12/month (VM) + $1/year (domain) = ~$13/month
- **With backups**: $14.40/month

---

## 🛠️ Tools You'll Need

### Required
- [ ] SSH client (Terminal on Mac/Linux, PuTTY on Windows)
- [ ] Text editor (nano, vim, or VS Code with Remote SSH)
- [ ] Web browser (Chrome, Firefox, or Edge)

### Optional but Helpful
- [ ] FileZilla or WinSCP (for file transfers)
- [ ] Postman or curl (for API testing)
- [ ] Git client (if using GitHub)

---

## 📝 Information to Gather

Before starting deployment, have these ready:

### Vultr VM Information (will get after creating VM)
```
VM IP Address: ___________________
Root Password: ___________________
SSH Port: 22 (default)
```

### API Keys
```
Google Gemini API Key: ___________________
```

### Domain Information (if using custom domain)
```
Domain Name: ___________________
Domain Registrar: ___________________
DNS Provider: ___________________
```

### Application URLs (after deployment)
```
Frontend URL: http://YOUR_VM_IP/login.html
API URL: http://YOUR_VM_IP/api/
API Docs: http://YOUR_VM_IP/docs
```

---

## 🎯 Deployment Strategy

### Choose Your Deployment Method

#### Method 1: Automated Script (Easiest)
**Best for:** Quick deployment, beginners
**Time:** 10-15 minutes
**Steps:**
1. Create Vultr VM
2. SSH into VM
3. Run `deploy_vultr.sh` script
4. Done!

#### Method 2: Manual Step-by-Step (Most Control)
**Best for:** Learning, customization
**Time:** 30-45 minutes
**Steps:**
1. Follow `VULTR_DEPLOYMENT_COMPLETE.md`
2. Execute each command manually
3. Understand each step

#### Method 3: Docker (Most Portable)
**Best for:** Containerized deployments
**Time:** 20-30 minutes
**Steps:**
1. Install Docker on VM
2. Build Docker image
3. Run container

---

## ⚠️ Common Pitfalls to Avoid

### Before Deployment
- [ ] Don't commit `.env` file to Git
- [ ] Don't use weak passwords
- [ ] Don't skip local testing
- [ ] Don't forget to backup important data

### During Deployment
- [ ] Don't close SSH session during updates
- [ ] Don't skip firewall configuration
- [ ] Don't forget to update `API_BASE` in frontend
- [ ] Don't use HTTP in production (use HTTPS)

### After Deployment
- [ ] Don't forget to test all features
- [ ] Don't ignore error logs
- [ ] Don't skip SSL certificate setup
- [ ] Don't forget to setup backups

---

## 📚 Documentation to Read

Before deploying, familiarize yourself with:

1. **VULTR_DEPLOYMENT_COMPLETE.md** - Full deployment guide
2. **DEPLOYMENT_QUICK_REFERENCE.md** - Command reference
3. **README.md** - Project overview
4. **SAAS_SETUP.md** - Authentication system

---

## 🧪 Test Plan After Deployment

After deployment, test these features:

### Authentication
- [ ] Can access login page
- [ ] Can create new account
- [ ] Can login with credentials
- [ ] Can logout
- [ ] Invalid credentials are rejected

### Non-Verbal to Verbal Mode
- [ ] Can start simulation
- [ ] Can click emoji buttons
- [ ] AI responds correctly
- [ ] Conversation history shows
- [ ] Can stop simulation

### Verbal to Non-Verbal Mode
- [ ] Can switch modes
- [ ] Can select common phrases
- [ ] Phrases translate to ASL emojis
- [ ] Translations are correct
- [ ] Conversation persists

### General
- [ ] Page loads quickly
- [ ] No console errors
- [ ] Mobile responsive (if applicable)
- [ ] All emojis display correctly
- [ ] Credits system works (for free users)

---

## 🚀 Ready to Deploy?

If you've checked all the boxes above, you're ready to deploy!

### Next Steps:

1. **Create Vultr VM**
   - Go to https://www.vultr.com
   - Click "Deploy New Server"
   - Follow Part 1 of `VULTR_DEPLOYMENT_COMPLETE.md`

2. **Choose Deployment Method**
   - Automated: Run `deploy_vultr.sh`
   - Manual: Follow `VULTR_DEPLOYMENT_COMPLETE.md`

3. **Test Deployment**
   - Access your application
   - Run through test plan
   - Verify everything works

4. **Setup SSL (Optional)**
   - Point domain to VM
   - Install SSL certificate
   - Update frontend to use HTTPS

5. **Monitor and Maintain**
   - Check logs regularly
   - Setup backups
   - Keep system updated

---

## 📞 Need Help?

If you get stuck:

1. **Check logs:**
   ```bash
   journalctl -u comm-bridge -n 100
   ```

2. **Review documentation:**
   - VULTR_DEPLOYMENT_COMPLETE.md
   - DEPLOYMENT_QUICK_REFERENCE.md

3. **Common issues:**
   - API key not set → Check `.env` file
   - Port in use → Kill existing process
   - Permission denied → Check file permissions
   - 502 Bad Gateway → Backend not running

---

## ✅ Final Checklist

Before clicking "Deploy":

- [ ] I have a Vultr account with payment method
- [ ] I have my Google Gemini API key
- [ ] My code is tested locally
- [ ] My code is pushed to GitHub (or ready to upload)
- [ ] I have read the deployment guide
- [ ] I have 30-60 minutes available
- [ ] I have SSH client ready
- [ ] I understand the costs involved
- [ ] I have a backup of my local database (if any)
- [ ] I'm ready to deploy! 🚀

---

**Good luck with your deployment!** 🎉

Once deployed, your Communication Bridge AI will be accessible 24/7 from anywhere in the world!

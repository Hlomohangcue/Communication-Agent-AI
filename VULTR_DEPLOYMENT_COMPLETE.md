# Complete Vultr VM Deployment Guide
## Communication Bridge AI - Production Deployment

This guide will walk you through deploying your Communication Bridge AI system to a Vultr VM from scratch.

---

## 📋 Prerequisites

Before starting, you'll need:
- [ ] Vultr account (sign up at https://www.vultr.com)
- [ ] Google Gemini API key (get from https://makersuite.google.com/app/apikey)
- [ ] Your project files ready (or GitHub repository URL)
- [ ] SSH client (Terminal on Mac/Linux, PuTTY on Windows)

---

## 🚀 Part 1: Create Vultr VM

### Step 1: Create New Server

1. Log into Vultr dashboard
2. Click **"Deploy New Server"** or **"+"** button
3. Choose **"Cloud Compute"**

### Step 2: Server Configuration

**Choose Server Location:**
- Select region closest to your users
- Recommended: New York, Los Angeles, or London

**Choose Server Type:**
- Select **"Ubuntu 22.04 LTS x64"**

**Choose Server Size:**
- **Minimum**: $6/month (1 vCPU, 1GB RAM, 25GB SSD)
- **Recommended**: $12/month (1 vCPU, 2GB RAM, 55GB SSD)
- **For production**: $24/month (2 vCPU, 4GB RAM, 80GB SSD)

**Additional Features (Optional):**
- ✅ Enable Auto Backups ($1.20/month)
- ✅ Enable IPv6
- ⬜ DDoS Protection (if needed)

**Server Hostname:**
- Enter: `comm-bridge-ai` or your preferred name

### Step 3: Deploy Server

1. Click **"Deploy Now"**
2. Wait 2-3 minutes for server to be ready
3. Note down:
   - **IP Address**: (e.g., 123.45.67.89)
   - **Username**: root
   - **Password**: (shown in server details)

---

## 🔐 Part 2: Initial Server Setup

### Step 1: Connect to Your VM

**On Mac/Linux:**
```bash
ssh root@YOUR_VM_IP
# Example: ssh root@123.45.67.89
```

**On Windows (using PuTTY):**
1. Open PuTTY
2. Enter IP address
3. Click "Open"
4. Login as: root
5. Enter password

**First Login:**
- Type `yes` when asked about fingerprint
- Enter the password from Vultr dashboard

### Step 2: Update System

```bash
# Update package lists
apt update

# Upgrade all packages
apt upgrade -y

# This may take 5-10 minutes
```

### Step 3: Create Swap File (for 1GB RAM servers)

```bash
# Create 2GB swap file
fallocate -l 2G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile

# Make swap permanent
echo '/swapfile none swap sw 0 0' | tee -a /etc/fstab

# Verify swap
free -h
```

### Step 4: Install Required Software

```bash
# Install Python, pip, git, and other essentials
apt install -y python3 python3-pip python3-venv git curl wget nano ufw

# Verify installations
python3 --version  # Should show Python 3.10+
pip3 --version
git --version
```

---

## 📦 Part 3: Deploy Application

### Option A: Deploy from GitHub (Recommended)

#### Step 1: Push Your Code to GitHub (if not already done)

**On your local machine:**
```bash
# Initialize git (if not already done)
cd /path/to/your/project
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit for deployment"

# Create repository on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git branch -M main
git push -u origin main
```

#### Step 2: Clone Repository on VM

**On your VM:**
```bash
# Navigate to home directory
cd ~

# Clone your repository
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git

# Navigate into project
cd YOUR_REPO

# Example:
# git clone https://github.com/yourusername/communication-bridge-ai.git
# cd communication-bridge-ai
```

### Option B: Upload Files Directly (Alternative)

**On your local machine:**
```bash
# Compress your project
tar -czf project.tar.gz /path/to/your/project

# Upload to VM using SCP
scp project.tar.gz root@YOUR_VM_IP:/root/

# On VM, extract:
ssh root@YOUR_VM_IP
cd ~
tar -xzf project.tar.gz
cd communication-bridge-ai
```

### Step 3: Install Python Dependencies

```bash
# Make sure you're in project directory
cd ~/communication-bridge-ai  # or your project name

# Install dependencies
pip3 install -r requirements.txt

# This will install:
# - FastAPI
# - Uvicorn
# - Google Generative AI
# - PyJWT, bcrypt (for authentication)
# - And other dependencies
```

### Step 4: Configure Environment Variables

```bash
# Create .env file
nano .env

# Add this content (replace with your actual API key):
GEMINI_API_KEY=your-actual-gemini-api-key-here

# Save and exit:
# Press Ctrl+X, then Y, then Enter
```

**To get your Gemini API key:**
1. Go to https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key
4. Paste it in the .env file

### Step 5: Test Backend Locally

```bash
# Navigate to backend directory
cd ~/communication-bridge-ai/backend

# Run backend
python3 main.py

# You should see:
# INFO:     Started server process
# INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Test in another terminal:**
```bash
# Open new SSH session
ssh root@YOUR_VM_IP

# Test API
curl http://localhost:8000/

# Should return: {"message": "Communication Bridge AI API", ...}
```

**Stop the test server:**
- Press `Ctrl+C` in the terminal running the backend

---

## 🔧 Part 4: Production Setup with Systemd

### Step 1: Create Systemd Service

```bash
# Create service file
nano /etc/systemd/system/comm-bridge.service
```

**Add this content:**
```ini
[Unit]
Description=Communication Bridge AI Backend
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/communication-bridge-ai/backend
Environment="PATH=/usr/local/bin:/usr/bin:/bin"
ExecStart=/usr/bin/python3 main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Save and exit** (Ctrl+X, Y, Enter)

### Step 2: Start Service

```bash
# Reload systemd
systemctl daemon-reload

# Enable service (start on boot)
systemctl enable comm-bridge

# Start service
systemctl start comm-bridge

# Check status
systemctl status comm-bridge

# Should show "active (running)" in green
```

### Step 3: View Logs

```bash
# View real-time logs
journalctl -u comm-bridge -f

# View last 100 lines
journalctl -u comm-bridge -n 100

# Press Ctrl+C to exit
```

---

## 🌐 Part 5: Configure Nginx Reverse Proxy

### Step 1: Install Nginx

```bash
# Install Nginx
apt install -y nginx

# Start Nginx
systemctl start nginx
systemctl enable nginx
```

### Step 2: Configure Nginx for Your App

```bash
# Remove default config
rm /etc/nginx/sites-enabled/default

# Create new config
nano /etc/nginx/sites-available/comm-bridge
```

**Add this content:**
```nginx
server {
    listen 80;
    server_name YOUR_VM_IP;  # Replace with your IP or domain

    # Increase upload size for file uploads
    client_max_body_size 10M;

    # Frontend files
    location / {
        root /root/communication-bridge-ai/frontend;
        index dashboard.html index.html;
        try_files $uri $uri/ =404;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # Direct backend access (for testing)
    location /docs {
        proxy_pass http://localhost:8000/docs;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
    }
}
```

**Save and exit** (Ctrl+X, Y, Enter)

### Step 3: Enable Site and Restart Nginx

```bash
# Enable site
ln -s /etc/nginx/sites-available/comm-bridge /etc/nginx/sites-enabled/

# Test configuration
nginx -t

# Should show: "syntax is ok" and "test is successful"

# Restart Nginx
systemctl restart nginx

# Check status
systemctl status nginx
```

---

## 🔥 Part 6: Configure Firewall

```bash
# Allow SSH (important - don't lock yourself out!)
ufw allow 22/tcp

# Allow HTTP
ufw allow 80/tcp

# Allow HTTPS (for future SSL)
ufw allow 443/tcp

# Enable firewall
ufw enable

# Type 'y' and press Enter

# Check status
ufw status

# Should show:
# Status: active
# 22/tcp    ALLOW    Anywhere
# 80/tcp    ALLOW    Anywhere
# 443/tcp   ALLOW    Anywhere
```

---

## 🎯 Part 7: Update Frontend API URL

### Step 1: Update app.js

```bash
# Edit app.js
nano ~/communication-bridge-ai/frontend/app.js
```

**Find this line (near the top):**
```javascript
const API_BASE = 'http://localhost:8000';
```

**Change to:**
```javascript
const API_BASE = 'http://YOUR_VM_IP/api';
// Example: const API_BASE = 'http://123.45.67.89/api';
```

**Or if using domain:**
```javascript
const API_BASE = 'http://yourdomain.com/api';
```

**Save and exit** (Ctrl+X, Y, Enter)

### Step 2: Restart Services

```bash
# Restart backend
systemctl restart comm-bridge

# Restart Nginx
systemctl restart nginx
```

---

## ✅ Part 8: Test Your Deployment

### Step 1: Test Backend API

```bash
# Test from VM
curl http://localhost:8000/

# Test from outside (replace with your IP)
curl http://YOUR_VM_IP/api/
```

### Step 2: Test Frontend

**Open in your browser:**
```
http://YOUR_VM_IP/login.html
```

**You should see:**
- Login page loads correctly
- No console errors (press F12 to check)
- Can create account and login

### Step 3: Test Full Workflow

1. **Create Account:**
   - Go to http://YOUR_VM_IP/login.html
   - Click "Sign Up"
   - Create account

2. **Login:**
   - Enter credentials
   - Should redirect to dashboard

3. **Test Communication:**
   - Click "Start Simulation"
   - Try sending a message with emoji gestures
   - Verify AI responds correctly

4. **Test Mode Switching:**
   - Switch between "Non-Verbal to Verbal" and "Verbal to Non-Verbal"
   - Verify conversation history persists

---

## 🔒 Part 9: Add SSL Certificate (Optional but Recommended)

### Prerequisites
- You need a domain name pointed to your VM IP

### Step 1: Point Domain to VM

1. Go to your domain registrar (GoDaddy, Namecheap, etc.)
2. Add an A record:
   - **Type**: A
   - **Name**: @ (or subdomain like `app`)
   - **Value**: YOUR_VM_IP
   - **TTL**: 3600

3. Wait 5-60 minutes for DNS propagation

### Step 2: Install Certbot

```bash
# Install Certbot
apt install -y certbot python3-certbot-nginx

# Get certificate
certbot --nginx -d yourdomain.com

# Follow prompts:
# - Enter email address
# - Agree to terms
# - Choose to redirect HTTP to HTTPS (option 2)
```

### Step 3: Update Frontend API URL

```bash
# Edit app.js
nano ~/communication-bridge-ai/frontend/app.js

# Change API_BASE to use HTTPS:
const API_BASE = 'https://yourdomain.com/api';

# Save and exit
```

### Step 4: Test HTTPS

```bash
# Restart services
systemctl restart comm-bridge
systemctl restart nginx

# Test in browser
# Go to: https://yourdomain.com/login.html
```

### Step 5: Auto-Renewal

```bash
# Test renewal
certbot renew --dry-run

# Certbot automatically sets up auto-renewal
# Certificates will renew automatically every 90 days
```

---

## 📊 Part 10: Monitoring and Maintenance

### Check Service Status

```bash
# Check backend
systemctl status comm-bridge

# Check Nginx
systemctl status nginx

# Check all services
systemctl list-units --type=service --state=running
```

### View Logs

```bash
# Backend logs (real-time)
journalctl -u comm-bridge -f

# Backend logs (last 100 lines)
journalctl -u comm-bridge -n 100

# Nginx access logs
tail -f /var/log/nginx/access.log

# Nginx error logs
tail -f /var/log/nginx/error.log

# System logs
tail -f /var/log/syslog
```

### Check Database

```bash
# Navigate to backend
cd ~/communication-bridge-ai/backend

# Open database
sqlite3 communication_bridge.db

# View tables
.tables

# View users
SELECT * FROM users;

# View sessions
SELECT * FROM sessions;

# Exit
.exit
```

### Monitor Resources

```bash
# Check disk space
df -h

# Check memory usage
free -h

# Check CPU usage
top

# Press 'q' to exit top

# Check running processes
ps aux | grep python
```

---

## 🔄 Part 11: Updating Your Application

### Method 1: Git Pull (if using GitHub)

```bash
# Navigate to project
cd ~/communication-bridge-ai

# Pull latest changes
git pull origin main

# Install any new dependencies
pip3 install -r requirements.txt

# Restart services
systemctl restart comm-bridge
systemctl restart nginx

# Check logs
journalctl -u comm-bridge -n 50
```

### Method 2: Manual Upload

```bash
# On local machine, upload new files
scp -r /path/to/updated/files root@YOUR_VM_IP:/root/communication-bridge-ai/

# On VM, restart services
systemctl restart comm-bridge
systemctl restart nginx
```

---

## 🐛 Troubleshooting

### Backend Won't Start

```bash
# Check logs
journalctl -u comm-bridge -n 100

# Common issues:
# 1. API key not set
cat ~/communication-bridge-ai/.env

# 2. Port already in use
lsof -i :8000
# Kill process if needed: kill -9 PID

# 3. Python dependencies missing
cd ~/communication-bridge-ai
pip3 install -r requirements.txt

# 4. Database locked
rm ~/communication-bridge-ai/backend/communication_bridge.db-journal
systemctl restart comm-bridge
```

### Frontend Not Loading

```bash
# Check Nginx status
systemctl status nginx

# Check Nginx configuration
nginx -t

# Check file permissions
ls -la ~/communication-bridge-ai/frontend/

# Fix permissions if needed
chmod -R 755 ~/communication-bridge-ai/frontend/

# Restart Nginx
systemctl restart nginx
```

### API Connection Errors

```bash
# Check if backend is running
curl http://localhost:8000/

# Check Nginx proxy
curl http://localhost/api/

# Check firewall
ufw status

# Check API_BASE in app.js
grep "API_BASE" ~/communication-bridge-ai/frontend/app.js
```

### Database Issues

```bash
# Backup database
cp ~/communication-bridge-ai/backend/communication_bridge.db ~/backup.db

# Check database integrity
cd ~/communication-bridge-ai/backend
sqlite3 communication_bridge.db "PRAGMA integrity_check;"

# Reset database (WARNING: deletes all data)
rm communication_bridge.db
systemctl restart comm-bridge
# Database will be recreated automatically
```

---

## 📈 Performance Optimization

### For Production Traffic

```bash
# Install Gunicorn for better performance
pip3 install gunicorn

# Update systemd service
nano /etc/systemd/system/comm-bridge.service

# Change ExecStart line to:
ExecStart=/usr/local/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker backend.main:app --bind 0.0.0.0:8000

# Reload and restart
systemctl daemon-reload
systemctl restart comm-bridge
```

### Enable Nginx Caching

```bash
# Edit Nginx config
nano /etc/nginx/sites-available/comm-bridge

# Add caching for static files:
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
    root /root/communication-bridge-ai/frontend;
    expires 1y;
    add_header Cache-Control "public, immutable";
}

# Restart Nginx
systemctl restart nginx
```

---

## 🎉 Success Checklist

- [ ] VM created and accessible via SSH
- [ ] System updated and dependencies installed
- [ ] Project files deployed (via Git or upload)
- [ ] Python dependencies installed
- [ ] .env file configured with API key
- [ ] Backend running as systemd service
- [ ] Nginx installed and configured
- [ ] Firewall configured (ports 22, 80, 443)
- [ ] Frontend API URL updated
- [ ] Can access login page in browser
- [ ] Can create account and login
- [ ] Can start simulation and send messages
- [ ] AI responds correctly to gestures
- [ ] Conversation history persists
- [ ] SSL certificate installed (if using domain)

---

## 🌟 Your Application is Live!

**Access your application at:**
- **Without domain**: http://YOUR_VM_IP/login.html
- **With domain**: https://yourdomain.com/login.html

**API Documentation:**
- http://YOUR_VM_IP/docs (FastAPI Swagger UI)

**Default Credentials:**
- Create new account on first visit

---

## 📞 Need Help?

**Common Commands Reference:**
```bash
# Restart backend
systemctl restart comm-bridge

# Restart Nginx
systemctl restart nginx

# View backend logs
journalctl -u comm-bridge -f

# Check all services
systemctl status

# Reboot VM
reboot
```

**Emergency Recovery:**
```bash
# If something goes wrong, you can always:
1. Stop services: systemctl stop comm-bridge nginx
2. Check logs: journalctl -u comm-bridge -n 200
3. Fix the issue
4. Restart: systemctl start comm-bridge nginx
```

---

## 🎊 Congratulations!

Your Communication Bridge AI is now deployed and running on Vultr! 

Users can access it 24/7 from anywhere in the world.

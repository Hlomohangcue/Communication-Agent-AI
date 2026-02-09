# Communication Bridge AI - Deployment Guide

## 🚀 Quick Start (Local Development)

### Prerequisites
- Python 3.11+
- pip package manager
- Google Gemini API key

### Setup Steps

1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

2. **Configure API Key**
```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your Gemini API key
GEMINI_API_KEY=your-actual-api-key-here
```

3. **Run Backend**
```bash
cd backend
python main.py
```

Backend will start on: `http://localhost:8000`

4. **Open Frontend**
- Open `frontend/dashboard.html` in your browser
- Or serve with: `python -m http.server 8080 --directory frontend`

## 🌐 Vultr VM Deployment

### Step 1: Create Vultr VM

1. Go to [Vultr.com](https://www.vultr.com)
2. Create new Cloud Compute instance
3. Choose:
   - **OS**: Ubuntu 22.04 LTS
   - **Plan**: $6/month (1 CPU, 1GB RAM) minimum
   - **Location**: Closest to your users

### Step 2: Connect to VM

```bash
ssh root@your-vm-ip-address
```

### Step 3: Install Dependencies

```bash
# Update system
apt update && apt upgrade -y

# Install Python and pip
apt install python3 python3-pip git -y

# Install Docker (optional but recommended)
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
```

### Step 4: Deploy Application

#### Option A: Docker Deployment (Recommended)

```bash
# Clone your repository
git clone <your-repo-url>
cd communication-bridge-ai

# Build Docker image
docker build -t comm-bridge .

# Run container
docker run -d \
  -p 80:8000 \
  -e GEMINI_API_KEY="your-api-key" \
  --name comm-bridge \
  --restart unless-stopped \
  comm-bridge

# Check logs
docker logs comm-bridge
```

#### Option B: Direct Deployment

```bash
# Clone repository
git clone <your-repo-url>
cd communication-bridge-ai

# Install dependencies
pip3 install -r requirements.txt

# Create .env file
echo "GEMINI_API_KEY=your-api-key-here" > .env

# Run with systemd (production)
# Create service file
cat > /etc/systemd/system/comm-bridge.service << EOF
[Unit]
Description=Communication Bridge AI
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/communication-bridge-ai/backend
Environment="PATH=/usr/bin"
ExecStart=/usr/bin/python3 main.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Start service
systemctl daemon-reload
systemctl enable comm-bridge
systemctl start comm-bridge

# Check status
systemctl status comm-bridge
```

### Step 5: Configure Firewall

```bash
# Allow HTTP and HTTPS
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 22/tcp
ufw enable
```

### Step 6: Setup Domain (Optional)

1. Point your domain to VM IP address
2. Install Nginx as reverse proxy:

```bash
apt install nginx -y

# Create Nginx config
cat > /etc/nginx/sites-available/comm-bridge << EOF
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
    }
}
EOF

# Enable site
ln -s /etc/nginx/sites-available/comm-bridge /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

3. Install SSL certificate (Let's Encrypt):

```bash
apt install certbot python3-certbot-nginx -y
certbot --nginx -d your-domain.com
```

## 🔧 Configuration

### Environment Variables

Create `.env` file in project root:

```env
GEMINI_API_KEY=your-google-gemini-api-key
```

### Database Configuration

Default: SQLite (`communication_bridge.db`)

For PostgreSQL (production scale):
1. Install PostgreSQL
2. Update `backend/database/db.py` connection string
3. Run migrations

## 📊 Monitoring

### Check Backend Status

```bash
# Docker
docker logs comm-bridge

# Systemd
journalctl -u comm-bridge -f

# Direct
curl http://localhost:8000/
```

### View Database

```bash
sqlite3 backend/communication_bridge.db
.tables
SELECT * FROM sessions;
```

## 🔄 Updates

### Docker

```bash
cd communication-bridge-ai
git pull
docker build -t comm-bridge .
docker stop comm-bridge
docker rm comm-bridge
docker run -d -p 80:8000 -e GEMINI_API_KEY="your-key" --name comm-bridge comm-bridge
```

### Direct

```bash
cd communication-bridge-ai
git pull
systemctl restart comm-bridge
```

## 🐛 Troubleshooting

### Backend won't start

```bash
# Check Python version
python3 --version  # Should be 3.11+

# Check dependencies
pip3 list

# Check logs
tail -f /var/log/syslog
```

### API Key Issues

```bash
# Verify API key is set
cat .env

# Test API key
python3 -c "import os; from config import GEMINI_API_KEY; print(GEMINI_API_KEY)"
```

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>
```

### Database Locked

```bash
# Stop all instances
systemctl stop comm-bridge
# Or
docker stop comm-bridge

# Remove lock
rm backend/communication_bridge.db-journal

# Restart
systemctl start comm-bridge
```

## 📈 Performance Optimization

### For High Traffic

1. **Use PostgreSQL** instead of SQLite
2. **Add Redis** for session caching
3. **Use Gunicorn** with multiple workers:

```bash
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker backend.main:app
```

4. **Enable Nginx caching**
5. **Use CDN** for static files

## 🔒 Security Best Practices

1. ✅ Never commit `.env` file
2. ✅ Use strong API keys
3. ✅ Enable firewall (ufw)
4. ✅ Use HTTPS in production
5. ✅ Regular security updates
6. ✅ Limit API rate limiting
7. ✅ Monitor logs for suspicious activity

## 📞 Support

For issues:
1. Check logs first
2. Review error messages
3. Verify API key is valid
4. Ensure all dependencies installed
5. Check firewall settings

## ✅ Deployment Checklist

- [ ] VM created and accessible
- [ ] Dependencies installed
- [ ] Repository cloned
- [ ] API key configured
- [ ] Backend running
- [ ] Frontend accessible
- [ ] Firewall configured
- [ ] Domain pointed (optional)
- [ ] SSL certificate installed (optional)
- [ ] Monitoring setup
- [ ] Backup strategy in place

## 🎉 Success!

Your Communication Bridge AI is now deployed and accessible at:
- **Local**: http://localhost:8000
- **VM**: http://your-vm-ip
- **Domain**: https://your-domain.com

Access the dashboard at: `/dashboard.html`

# Deployment Quick Reference Card

## 🚀 Quick Deploy (Automated)

```bash
# On your Vultr VM (as root):
wget https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/deploy_vultr.sh
chmod +x deploy_vultr.sh
./deploy_vultr.sh
```

Or upload the script and run:
```bash
bash deploy_vultr.sh
```

---

## 📋 Manual Deploy Commands

### Initial Setup
```bash
# Update system
apt update && apt upgrade -y

# Install dependencies
apt install -y python3 python3-pip git nginx ufw

# Clone project
cd ~
git clone YOUR_REPO_URL
cd communication-bridge-ai

# Install Python packages
pip3 install -r requirements.txt

# Configure API key
echo "GEMINI_API_KEY=your-key-here" > .env
```

### Start Backend
```bash
# Quick test
cd ~/communication-bridge-ai/backend
python3 main.py

# Production (systemd)
systemctl start comm-bridge
systemctl enable comm-bridge
```

### Configure Nginx
```bash
# Copy config
cp nginx.conf /etc/nginx/sites-available/comm-bridge
ln -s /etc/nginx/sites-available/comm-bridge /etc/nginx/sites-enabled/

# Test and restart
nginx -t
systemctl restart nginx
```

### Firewall
```bash
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
```

---

## 🔧 Common Commands

### Service Management
```bash
# Start/Stop/Restart
systemctl start comm-bridge
systemctl stop comm-bridge
systemctl restart comm-bridge

# Check status
systemctl status comm-bridge

# Enable/Disable auto-start
systemctl enable comm-bridge
systemctl disable comm-bridge
```

### View Logs
```bash
# Backend logs (real-time)
journalctl -u comm-bridge -f

# Last 100 lines
journalctl -u comm-bridge -n 100

# Nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### Update Application
```bash
# Pull latest code
cd ~/communication-bridge-ai
git pull

# Restart services
systemctl restart comm-bridge
systemctl restart nginx
```

### Database Management
```bash
# Open database
cd ~/communication-bridge-ai/backend
sqlite3 communication_bridge.db

# View tables
.tables

# View users
SELECT * FROM users;

# Backup database
cp communication_bridge.db ~/backup_$(date +%Y%m%d).db
```

---

## 🐛 Troubleshooting

### Backend Won't Start
```bash
# Check logs
journalctl -u comm-bridge -n 100

# Check if port is in use
lsof -i :8000

# Verify API key
cat ~/communication-bridge-ai/.env

# Test manually
cd ~/communication-bridge-ai/backend
python3 main.py
```

### Frontend Not Loading
```bash
# Check Nginx
systemctl status nginx
nginx -t

# Check file permissions
ls -la ~/communication-bridge-ai/frontend/

# Fix permissions
chmod -R 755 ~/communication-bridge-ai/frontend/
```

### API Connection Issues
```bash
# Test backend locally
curl http://localhost:8000/

# Test through Nginx
curl http://localhost/api/

# Check API_BASE in frontend
grep "API_BASE" ~/communication-bridge-ai/frontend/app.js
```

---

## 📊 Monitoring

### Check Resources
```bash
# Disk space
df -h

# Memory
free -h

# CPU and processes
top
htop  # if installed

# Network
netstat -tulpn | grep LISTEN
```

### Check Services
```bash
# All services
systemctl list-units --type=service --state=running

# Specific service
systemctl status comm-bridge
systemctl status nginx
```

---

## 🔒 Security

### Update System
```bash
apt update
apt upgrade -y
apt autoremove -y
```

### Check Firewall
```bash
ufw status verbose
```

### SSL Certificate (with domain)
```bash
# Install Certbot
apt install -y certbot python3-certbot-nginx

# Get certificate
certbot --nginx -d yourdomain.com

# Test renewal
certbot renew --dry-run
```

---

## 🔄 Backup & Restore

### Backup
```bash
# Backup database
cp ~/communication-bridge-ai/backend/communication_bridge.db ~/backup.db

# Backup entire project
tar -czf ~/comm-bridge-backup-$(date +%Y%m%d).tar.gz ~/communication-bridge-ai/

# Download backup to local machine
scp root@YOUR_VM_IP:~/backup.db ./local-backup.db
```

### Restore
```bash
# Restore database
cp ~/backup.db ~/communication-bridge-ai/backend/communication_bridge.db
systemctl restart comm-bridge
```

---

## 📱 Access URLs

### Without Domain
- Frontend: `http://YOUR_VM_IP/login.html`
- Dashboard: `http://YOUR_VM_IP/dashboard.html`
- API Docs: `http://YOUR_VM_IP/docs`
- API Base: `http://YOUR_VM_IP/api/`

### With Domain
- Frontend: `https://yourdomain.com/login.html`
- Dashboard: `https://yourdomain.com/dashboard.html`
- API Docs: `https://yourdomain.com/docs`
- API Base: `https://yourdomain.com/api/`

---

## 🆘 Emergency Recovery

### Complete Restart
```bash
systemctl stop comm-bridge
systemctl stop nginx
systemctl start comm-bridge
systemctl start nginx
```

### Reset Database (WARNING: Deletes all data)
```bash
systemctl stop comm-bridge
rm ~/communication-bridge-ai/backend/communication_bridge.db
systemctl start comm-bridge
```

### Reboot VM
```bash
reboot
```

---

## 📞 Quick Help

### Get VM IP
```bash
curl ifconfig.me
```

### Test Backend
```bash
curl http://localhost:8000/
```

### Check Python Version
```bash
python3 --version
```

### Check Installed Packages
```bash
pip3 list
```

### View Environment Variables
```bash
cat ~/communication-bridge-ai/.env
```

---

## 🎯 Performance Tips

### Use Gunicorn (Production)
```bash
pip3 install gunicorn

# Update systemd service ExecStart:
ExecStart=/usr/local/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker backend.main:app --bind 0.0.0.0:8000

systemctl daemon-reload
systemctl restart comm-bridge
```

### Enable Nginx Caching
Add to Nginx config:
```nginx
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

### Monitor Performance
```bash
# Install monitoring tools
apt install -y htop iotop nethogs

# Use them
htop      # CPU and memory
iotop     # Disk I/O
nethogs   # Network usage
```

---

## ✅ Health Check Script

Create `health_check.sh`:
```bash
#!/bin/bash
echo "=== System Health Check ==="
echo "Backend: $(systemctl is-active comm-bridge)"
echo "Nginx: $(systemctl is-active nginx)"
echo "Disk: $(df -h / | tail -1 | awk '{print $5}')"
echo "Memory: $(free -h | grep Mem | awk '{print $3 "/" $2}')"
echo "API: $(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/)"
```

Run with: `bash health_check.sh`

---

## 📚 Documentation Files

- `VULTR_DEPLOYMENT_COMPLETE.md` - Full deployment guide
- `DEPLOYMENT_GUIDE.md` - General deployment info
- `README.md` - Project overview
- `SAAS_SETUP.md` - Authentication setup
- `EMOJI_FIX_SUMMARY.md` - Recent emoji updates

---

## 🎉 Success Indicators

✅ `systemctl status comm-bridge` shows "active (running)"
✅ `systemctl status nginx` shows "active (running)"
✅ `curl http://localhost:8000/` returns JSON
✅ Browser can access `http://YOUR_VM_IP/login.html`
✅ Can create account and login
✅ Can send messages and get AI responses

---

**Need more help?** See `VULTR_DEPLOYMENT_COMPLETE.md` for detailed instructions.

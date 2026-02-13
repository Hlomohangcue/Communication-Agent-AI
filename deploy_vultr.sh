#!/bin/bash

# Communication Bridge AI - Vultr Deployment Script
# This script automates the deployment process on a fresh Ubuntu 22.04 VM

set -e  # Exit on any error

echo "=========================================="
echo "Communication Bridge AI - Vultr Deployment"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    print_error "Please run as root (use: sudo bash deploy_vultr.sh)"
    exit 1
fi

print_info "Starting deployment process..."
echo ""

# Step 1: Update system
print_info "Step 1/10: Updating system packages..."
apt update -qq
apt upgrade -y -qq
print_success "System updated"
echo ""

# Step 2: Install dependencies
print_info "Step 2/10: Installing dependencies..."
apt install -y -qq python3 python3-pip python3-venv git curl wget nano ufw nginx sqlite3
print_success "Dependencies installed"
echo ""

# Step 3: Create swap file (for low memory VMs)
print_info "Step 3/10: Creating swap file..."
if [ ! -f /swapfile ]; then
    fallocate -l 2G /swapfile
    chmod 600 /swapfile
    mkswap /swapfile > /dev/null 2>&1
    swapon /swapfile
    echo '/swapfile none swap sw 0 0' | tee -a /etc/fstab > /dev/null
    print_success "Swap file created (2GB)"
else
    print_info "Swap file already exists"
fi
echo ""

# Step 4: Get project location
print_info "Step 4/10: Setting up project..."
read -p "Enter GitHub repository URL (or press Enter to skip): " REPO_URL

if [ -z "$REPO_URL" ]; then
    print_info "Skipping Git clone. Please upload your files manually to /root/communication-bridge-ai"
    PROJECT_DIR="/root/communication-bridge-ai"
else
    cd /root
    if [ -d "communication-bridge-ai" ]; then
        print_info "Project directory exists. Pulling latest changes..."
        cd communication-bridge-ai
        git pull
    else
        print_info "Cloning repository..."
        git clone "$REPO_URL" communication-bridge-ai
        cd communication-bridge-ai
    fi
    PROJECT_DIR="/root/communication-bridge-ai"
    print_success "Project files ready"
fi
echo ""

# Step 5: Install Python dependencies
print_info "Step 5/10: Installing Python dependencies..."
cd "$PROJECT_DIR"
if [ -f "requirements.txt" ]; then
    pip3 install -q -r requirements.txt
    print_success "Python dependencies installed"
else
    print_error "requirements.txt not found. Please ensure project files are in $PROJECT_DIR"
    exit 1
fi
echo ""

# Step 6: Configure environment
print_info "Step 6/10: Configuring environment..."
if [ ! -f ".env" ]; then
    read -p "Enter your Google Gemini API key: " API_KEY
    echo "GEMINI_API_KEY=$API_KEY" > .env
    print_success "Environment configured"
else
    print_info ".env file already exists"
fi
echo ""

# Step 7: Create systemd service
print_info "Step 7/10: Creating systemd service..."
cat > /etc/systemd/system/comm-bridge.service << EOF
[Unit]
Description=Communication Bridge AI Backend
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$PROJECT_DIR/backend
Environment="PATH=/usr/local/bin:/usr/bin:/bin"
ExecStart=/usr/bin/python3 main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable comm-bridge
systemctl start comm-bridge
print_success "Backend service created and started"
echo ""

# Step 8: Configure Nginx
print_info "Step 8/10: Configuring Nginx..."

# Get server IP
SERVER_IP=$(curl -s ifconfig.me)

# Remove default config
rm -f /etc/nginx/sites-enabled/default

# Create new config
cat > /etc/nginx/sites-available/comm-bridge << EOF
server {
    listen 80;
    server_name $SERVER_IP;

    client_max_body_size 10M;

    # Frontend files
    location / {
        root $PROJECT_DIR/frontend;
        index login.html dashboard.html index.html;
        try_files \$uri \$uri/ =404;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
    }

    # API docs
    location /docs {
        proxy_pass http://localhost:8000/docs;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
    }
}
EOF

# Enable site
ln -sf /etc/nginx/sites-available/comm-bridge /etc/nginx/sites-enabled/

# Test and restart Nginx
nginx -t
systemctl restart nginx
print_success "Nginx configured and restarted"
echo ""

# Step 9: Configure firewall
print_info "Step 9/10: Configuring firewall..."
ufw --force enable
ufw allow 22/tcp > /dev/null 2>&1
ufw allow 80/tcp > /dev/null 2>&1
ufw allow 443/tcp > /dev/null 2>&1
print_success "Firewall configured"
echo ""

# Step 10: Update frontend API URL
print_info "Step 10/10: Updating frontend configuration..."
if [ -f "$PROJECT_DIR/frontend/app.js" ]; then
    # Backup original
    cp "$PROJECT_DIR/frontend/app.js" "$PROJECT_DIR/frontend/app.js.backup"
    
    # Update API_BASE
    sed -i "s|const API_BASE = 'http://localhost:8000';|const API_BASE = 'http://$SERVER_IP/api';|g" "$PROJECT_DIR/frontend/app.js"
    print_success "Frontend configured"
else
    print_error "app.js not found. Please update API_BASE manually"
fi
echo ""

# Final checks
print_info "Running final checks..."
sleep 3

# Check backend status
if systemctl is-active --quiet comm-bridge; then
    print_success "Backend service is running"
else
    print_error "Backend service failed to start. Check logs with: journalctl -u comm-bridge -n 50"
fi

# Check Nginx status
if systemctl is-active --quiet nginx; then
    print_success "Nginx is running"
else
    print_error "Nginx failed to start. Check logs with: journalctl -u nginx -n 50"
fi

# Test backend API
if curl -s http://localhost:8000/ > /dev/null; then
    print_success "Backend API is responding"
else
    print_error "Backend API is not responding"
fi

echo ""
echo "=========================================="
echo "🎉 Deployment Complete!"
echo "=========================================="
echo ""
echo "Your application is now live at:"
echo "  📱 Frontend: http://$SERVER_IP/login.html"
echo "  🔧 API Docs: http://$SERVER_IP/docs"
echo ""
echo "Useful commands:"
echo "  • View backend logs:  journalctl -u comm-bridge -f"
echo "  • Restart backend:    systemctl restart comm-bridge"
echo "  • Restart Nginx:      systemctl restart nginx"
echo "  • Check status:       systemctl status comm-bridge"
echo ""
echo "Next steps:"
echo "  1. Visit http://$SERVER_IP/login.html"
echo "  2. Create a new account"
echo "  3. Start using the Communication Bridge AI!"
echo ""
echo "For SSL/HTTPS setup with a domain, see: VULTR_DEPLOYMENT_COMPLETE.md"
echo "=========================================="

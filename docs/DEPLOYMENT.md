# Deployment Guide

Primary deployment strategy: self-hosted laptop + Docker + Cloudflare Tunnel

Alternative strategy still available: VPS deployment assets (for example deploy_vultr.sh and nginx.conf)

## LOCAL DEPLOYMENT (SELF-HOSTED BASELINE)

### 1) Laptop prerequisites
- Linux host preferred for 24/7 operation.
- Docker Engine and Docker Compose plugin installed.
- Stable internet connection.
- Persistent host storage for database backups.

### 2) Create environment file
Create .env from .env.example and set production-safe values.

Required for production:
- APP_ENV=production
- JWT_SECRET_KEY=<strong random secret>
- GEMINI_API_KEY=<your key>
- CORS_ORIGINS=https://bridge.slimeshustlers.com
- CORS_ALLOW_CREDENTIALS=true

Recommended database path for containerized deployment:
- DATABASE_PATH=/app/data/communication_bridge.db

### 3) Build the container
```bash
docker compose build
```

### 4) Start the application
```bash
docker compose up -d
```

The compose service binds to localhost only:
- http://127.0.0.1:8000

### 5) Verify backend health
```bash
curl http://127.0.0.1:8000/health
```

Expected HTTP 200 response includes status, app, and version.

### 6) Verify root endpoint
```bash
curl http://127.0.0.1:8000/
```

### 7) Verify frontend locally
Open:
- http://127.0.0.1:8000/app/login.html

Notes:
- Frontend now uses same-origin API routing by default.
- frontend/test.html is a development utility page and is not production-facing.

### 8) Verify authentication flow
1. Sign up from /app/login.html.
2. Log in and confirm redirect to dashboard.
3. Confirm protected requests succeed after login.

### 9) Verify vision functionality
1. Open webcam mode in dashboard.
2. Allow browser camera permission.
3. Confirm gesture processing endpoints return responses.

### 10) Verify SQLite persistence
Data is stored at DATABASE_PATH (default /app/data/communication_bridge.db in container).

Persistence check:
1. Create a user/session.
2. Restart or recreate the container.
3. Confirm the data remains.

### 11) Run 24/7 with automatic restart
- Compose restart policy is unless-stopped.
- Configure Docker daemon to start on host boot.

### 12) Backups
- Schedule periodic backup copies of the SQLite file.
- Store backups outside the container writable layer.
- Periodically test restore flow.

### 13) Troubleshooting quick checks
- Container logs:
```bash
docker compose logs -f
```
- Container health:
```bash
docker ps
```
- API health:
```bash
curl http://127.0.0.1:8000/health
```

### 14) Rollback
1. Keep prior known-good image tag and env snapshot.
2. Stop current container.
3. Start prior version with the same persistent volume.
4. Re-run health and auth smoke tests.

## CLOUDFLARE TUNNEL SETUP (MANUAL EXTERNAL PUBLICATION STEP)

This repository does not configure Cloudflare automatically.

Expected tunnel mapping for this project:
- Tunnel hostname: bridge.slimeshustlers.com
- Local service URL target: http://localhost:8000

Key tunnel properties:
- No inbound router port forwarding required.
- No direct public IP exposure required.
- Public HTTPS is provided by Cloudflare edge.

High-level manual steps:
1. Install and authenticate cloudflared on the host.
2. Create a tunnel in Cloudflare.
3. Map bridge.slimeshustlers.com to http://localhost:8000.
4. Run cloudflared as a managed service with auto-restart.
5. Validate public access and end-to-end auth/vision flows.

Important:
- Do not store Cloudflare API credentials in this repository.
- Keep slimeshustlers.com routing unchanged; only bridge.slimeshustlers.com should target this app.

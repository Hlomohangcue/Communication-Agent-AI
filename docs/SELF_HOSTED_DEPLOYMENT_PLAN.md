# Self-Hosted Deployment Plan

Date: 2026-07-21
Repository: Communication-Agent-AI
Scope: Read-only investigation and planning for self-hosted production demo deployment at https://bridge.slimeshustlers.com

## 1. Executive Summary
The application can be deployed publicly from a self-hosted laptop using Cloudflare Tunnel, but it is not yet safe/reliable enough to launch without targeted deployment fixes.

Current status: READY AFTER FIXES

Why:
- Current frontend has hardcoded fallback API URLs that do not match the target domain by default.
- Current deployment assets are VPS-oriented and include root-run service and HTTP-first assumptions.
- SQLite persistence is not explicitly planned for container lifecycle events.
- MediaPipe/OpenCV runtime compatibility in Docker must be validated on the target host.

## 2. Target Architecture
Intended target:

Browser
-> Cloudflare DNS and edge
-> Cloudflare Tunnel (cloudflared connector on laptop)
-> laptop local service
-> Dockerized Communication Bridge AI
-> FastAPI backend + SQLite + Gemini integration + vision processing

Target hostnames:
- https://slimeshustlers.com (existing site, unchanged)
- https://bridge.slimeshustlers.com (Communication Bridge AI Agent)

## 3. Current Application Architecture
### Frontend architecture
- Static frontend in frontend/ (HTML/CSS/JS).
- Main runtime files: frontend/login.html, frontend/dashboard.html, frontend/auth.js, frontend/app.js.
- API calls are generated from API_BASE in frontend JS.

### Backend architecture
- FastAPI app in backend/main.py.
- Route groups: auth, simulation, communication, logs/session, gesture translation, vision.
- Root endpoint / exists and returns status/version.
- No dedicated /health endpoint currently.

### API routing
- Backend routes are mounted directly (for example /auth/login, /simulate/start, /vision/process-frame).
- Backend does not mount static frontend routes (no StaticFiles mount found).

### Authentication
- JWT-based auth in backend/auth/auth_handler.py.
- Protected routes use Authorization: Bearer token in backend/main.py dependency.
- Tokens are stored client-side in localStorage/sessionStorage.

### Database
- SQLite is used via backend/database/db.py.
- DB file defaults to communication_bridge.db.
- Path is relative to process working directory.

### LLM integration
- Gemini integration is centralized in backend/services/llm_client.py.
- If GEMINI_API_KEY missing or package unavailable, fallback logic is used in agents.

### Vision pipeline
- backend/services/vision_service.py uses mediapipe + opencv-python.
- Browser sends frame data to backend; backend processes landmarks and returns gestures/emojis.

### Static frontend serving
- Backend does not currently serve frontend files.
- nginx.conf is designed to serve frontend static files and proxy /api to backend.

### Current Docker behavior
- Dockerfile builds a Python 3.11-slim image.
- Installs requirements.txt.
- Copies backend/ and frontend/ into image.
- Starts uvicorn backend.main:app on port 8000.
- Frontend is copied but not served by FastAPI.

### Current Nginx behavior
- nginx.conf serves frontend from filesystem root path and proxies API/docs/openapi to backend.
- Includes /api rewrite style expected by that Nginx topology.

## 4. Cloudflare Tunnel Architecture
Cloudflare Tunnel requirements for this deployment:
- Public hostname: bridge.slimeshustlers.com
- Local service URL: should point to the local web entrypoint (recommended: Nginx service URL)

Confirmed behavior from Cloudflare docs:
- Tunnel uses outbound-only connections from cloudflared to Cloudflare.
- No inbound router port forwarding is required.
- No direct exposure of laptop public IP is required.
- Cloudflare edge handles public HTTPS for the hostname.

Operational expectations:
- cloudflared must stay running on the laptop.
- laptop firewall should allow required outbound connectivity for cloudflared.
- local origin service can remain private (not internet-exposed directly).

## 5. Domain and API Routing
Intended domain split:
- slimeshustlers.com: existing main website
- bridge.slimeshustlers.com: Communication Bridge AI Agent

Current frontend API config issue:
- frontend/app.js and frontend/auth.js default API_BASE to a legacy external URL (brevlab domain).
- frontend/test.html also contains hardcoded external API_BASE.

Impact:
- Without explicit override, production frontend may call the wrong backend.

Clean strategy for target domain:
- Serve frontend and backend under bridge.slimeshustlers.com via one local web entrypoint.
- Use same-origin API_BASE (or explicit https://bridge.slimeshustlers.com/api with matching proxy).
- Avoid environment-specific string rewrites in ad-hoc scripts.

## 6. Docker Readiness
### Confirmed issues
- Frontend files in image are not served by backend runtime.
- No non-root runtime user is configured.
- No image healthcheck is defined.
- No explicit persistence strategy for communication_bridge.db.

### Likely issues
- OpenCV/MediaPipe may require additional Linux system libs beyond current slim image.
- Vision feature behavior may differ by host runtime graphics/system libraries.

### Items requiring runtime testing
- Container startup with mediapipe==0.10.8 and opencv-python on target host.
- Vision endpoint behavior (/vision/process-frame and /vision/interpret-gesture).
- End-to-end frontend access path through chosen local web entrypoint.

Python version note:
- Python 3.11 is appropriate for this project baseline (aligned with CI and local compatibility notes).

Current CMD correctness:
- CMD using uvicorn backend.main:app is correct for backend startup.

## 7. SQLite Persistence
DB file location:
- communication_bridge.db is created in the backend process working directory.
- In Docker, this means inside container filesystem unless volume-mounted.

Behavior by event:
- Container restart: data usually persists if same container filesystem remains.
- Image rebuild: old container filesystem is not part of new image.
- Container remove/recreate without volume: data loss.
- Laptop restart: depends on Docker restart policy and container persistence.
- Docker daemon restart: container may restart, but ephemeral data risk remains if container recreated.

Recommended persistence strategy (single-instance portfolio demo):
- Use a named Docker volume or bind mount for DB file directory.
- Keep backups via scheduled DB file copy/export.
- Store backups outside container writable layer.

Priority goals:
- Simplicity: single writer SQLite.
- Data safety: persistent mounted storage.
- Easy backup/restore: regular file-level backup snapshots.

## 8. MediaPipe/OpenCV Compatibility
### Compatibility
- Python compatibility: repository targets Python 3.11 baseline; newer versions may have package availability differences.
- Linux compatibility: likely workable, but slim images often need extra runtime libs.
- Docker compatibility: possible but not guaranteed without host/image runtime validation.

### Webcam architecture
- Browser captures webcam (navigator.mediaDevices.getUserMedia).
- Browser sends frame payloads to backend API.
- Backend does not need direct physical camera device access for normal web workflow.

Implication:
- Self-hosted laptop does not need an attached physical webcam for end users to use webcam mode.
- Users grant camera permissions in their own browser; backend processes uploaded frames.

Must-test items before public launch:
- End-to-end vision endpoint latency and reliability in deployed container.
- Browser permissions flow over HTTPS.
- CPU impact under repeated frame processing.

## 9. Security Assessment
Classification: BLOCKER/HIGH/MEDIUM/LOW

### BLOCKER
1. API base defaults to legacy external host in frontend JS.
- Risk: public demo can call wrong API endpoint.

2. Production secret posture not guaranteed by deployment assets.
- APP_ENV must be production.
- JWT_SECRET_KEY must be strong and private.

3. HTTPS-only browser path not yet operationally guaranteed.
- Webcam/mic UX and auth should run on secure origin.

### HIGH
1. Token storage in localStorage/sessionStorage increases XSS exposure impact.
2. No explicit rate limiting in app or edge config in repository defaults.
3. Docker image currently runs as root by default.
4. No dedicated app health endpoint for precise monitoring.

### MEDIUM
1. CORS defaults are localhost values and must be replaced for production.
2. SQLite backup/restore process is not yet automated in repository deployment assets.
3. Nginx and deploy script configurations are not yet aligned to self-hosted tunnel topology.

### LOW
1. Security headers exist in nginx.conf but need consistency with final deployment path.
2. Documentation drift from legacy VPS strategy can cause operator error.

Required production security settings:
- APP_ENV=production
- JWT_SECRET_KEY=<strong random value>
- CORS_ORIGINS=https://bridge.slimeshustlers.com (and only necessary origins)
- CORS_ALLOW_CREDENTIALS=true (if auth headers/cookies need it)
- GEMINI_API_KEY set via secure local secret handling

Cloudflare Tunnel security notes:
- Prefer no direct inbound exposure to origin.
- Keep cloudflared and host OS updated.
- Restrict local service bindings and host firewall rules.

## 10. Laptop Hosting Requirements
Practical minimum guidance for a 24/7 portfolio demo:
- CPU: modern multi-core CPU recommended (vision processing is CPU-intensive).
- RAM: enough headroom for OS + Docker + Python vision stack under active sessions.
- Storage: SSD strongly recommended, with space for DB, logs, and backups.
- Network: stable internet with reliable upstream bandwidth and low interruption frequency.
- Reliability: continuous power preferred (UPS strongly recommended).
- OS: Linux is preferred for Docker + cloudflared operational consistency.
- Autostart: host should auto-restart Docker and tunnel services after reboot/power outage.

## 11. Reliability and Operations
Simple reliable model recommended:
- Run app in Docker with restart policy (always/unless-stopped).
- Run cloudflared as a managed service with auto-restart.
- Keep one app instance (SQLite single writer).
- Monitor service health via root endpoint and process checks.
- Use log rotation for container and tunnel logs.
- Schedule regular SQLite backups to host path.
- Keep a restore drill procedure tested.

Handle common incidents:
- Laptop reboot: services should auto-start.
- Internet interruption: cloudflared reconnect behavior should be monitored.
- Docker/container crash: restart policy recovers service.
- Tunnel crash: service manager restarts cloudflared.

## 12. Deployment Phases
### Phase 1 - Application hardening
Objective:
- Remove configuration risks before public exposure.

Required changes:
- Fix frontend API base strategy for bridge.slimeshustlers.com.
- Enforce production env values and secrets handling.

Dependencies:
- Finalized domain decision and local web entrypoint.

Validation steps:
- Confirm frontend requests target correct domain/API paths.
- Verify auth and CORS behavior.

Potential blockers:
- Legacy hardcoded URLs still present in active frontend bundle.

### Phase 2 - Docker validation
Objective:
- Validate container runtime behavior on host OS.

Required changes:
- Add required runtime libraries if vision stack fails.
- Improve container security posture (non-root, healthcheck).

Dependencies:
- Access to target laptop Docker runtime.

Validation steps:
- Container starts cleanly.
- API root responds.
- Vision endpoints execute successfully.

Potential blockers:
- MediaPipe/OpenCV runtime incompatibilities.

### Phase 3 - Local production testing
Objective:
- Verify full app flow locally before tunnel publication.

Required changes:
- Confirm frontend static serving and API proxy behavior.

Dependencies:
- Local reverse proxy and backend connectivity.

Validation steps:
- Signup/login/session/vision flows pass locally.

Potential blockers:
- Path rewrite mismatch (/api vs direct routes).

### Phase 4 - Persistent storage
Objective:
- Ensure SQLite durability across lifecycle events.

Required changes:
- Configure Docker volume/bind mount for DB.
- Configure backup destination and schedule.

Dependencies:
- Stable host storage path.

Validation steps:
- Data survives container recreate and host reboot tests.

Potential blockers:
- Volume mount misconfiguration.

### Phase 5 - Cloudflare Tunnel setup
Objective:
- Publish bridge.slimeshustlers.com without exposing origin IP.

Required changes:
- Create tunnel and map hostname to local service URL.

Dependencies:
- Cloudflare zone control for slimeshustlers.com.

Validation steps:
- Public hostname resolves and routes correctly through tunnel.

Potential blockers:
- Tunnel connector instability or hostname routing misconfig.

### Phase 6 - Domain configuration
Objective:
- Keep domain architecture clean between main site and bridge subdomain.

Required changes:
- Ensure bridge.slimeshustlers.com route only maps to communication app.

Dependencies:
- Existing main website DNS preserved.

Validation steps:
- slimeshustlers.com unaffected.
- bridge subdomain serves app only.

Potential blockers:
- DNS conflicts or accidental record overlap.

### Phase 7 - Public testing
Objective:
- Verify real-user behavior from internet clients.

Required changes:
- None beyond final config tuning.

Dependencies:
- Tunnel healthy, HTTPS active, app reachable.

Validation steps:
- Cross-device/browser tests for login, API, webcam, mic permissions.

Potential blockers:
- Browser permission edge cases, CORS misconfig.

### Phase 8 - Monitoring and backups
Objective:
- Sustain reliable 24/7 service.

Required changes:
- Implement lightweight monitoring and backup schedule.

Dependencies:
- Host cron/task scheduler and log retention policy.

Validation steps:
- Alerts/log checks operational.
- Restore from backup tested.

Potential blockers:
- Backup failures or disk growth due to logs.

## 13. Vultr-to-Self-Hosted Migration
### Still useful
- Dockerfile baseline for backend container.
- nginx.conf as starting reverse-proxy/static hosting template.
- docs/DEPLOYMENT.md high-level deployment guidance.
- docs/DEPLOYMENT_READINESS_AUDIT.md as risk inventory baseline.

### Needs modification for new strategy
- deploy_vultr.sh: VPS/root/systemd assumptions and API rewrite logic.
- nginx.conf: host paths and final local service wiring for tunnel-based topology.
- docs/DEPLOYMENT.md: currently too generic for tunnel-based self-hosting runbook.

### No longer primary
- Vultr-specific provisioning flow in deploy_vultr.sh for this target architecture.

### Should be replaced by new canonical guidance
- Self-hosted runbook based on Docker + Cloudflare Tunnel + persistent SQLite storage.

## 14. Pre-Deployment Checklist
- Confirm bridge.slimeshustlers.com ownership under Cloudflare.
- Confirm production .env values and secret generation process.
- Confirm frontend API base strategy points to bridge domain.
- Confirm Docker image builds and starts on target laptop.
- Confirm local static frontend + API routing model.
- Confirm SQLite volume mount and backup path.
- Confirm cloudflared service autostart and health checks.
- Confirm host OS patch level and firewall posture.

## 15. Post-Deployment Testing Checklist
- Open https://bridge.slimeshustlers.com and verify frontend loads.
- Verify signup/login and token-protected endpoints.
- Verify GET / returns status JSON.
- Verify simulate/session/log routes with auth.
- Verify /vision/process-frame and /vision/interpret-gesture behavior.
- Verify CORS only allows intended origin(s).
- Verify data persists after container restart.
- Verify data persists after laptop reboot.
- Verify cloudflared reconnect after network flap.

## 16. Backup and Recovery Plan
Backup strategy (simple):
- Daily SQLite backup copy to host backup directory.
- Keep rolling retention snapshots (for example, 7-30 days based on disk budget).
- Periodically copy backups to secondary storage.

Recovery:
1. Stop app container.
2. Restore chosen DB backup to mounted persistent DB path.
3. Start container.
4. Run smoke tests (auth, session, vision).
5. Verify recent data integrity.

## 17. Rollback Plan
If a deployment update fails:
1. Keep previous known-good container image tag and config snapshot.
2. Stop failed container.
3. Start previous image with previous environment and same DB volume.
4. Validate root/auth/session endpoints.
5. Validate tunnel route is healthy.
6. Document incident and perform controlled retry.

## 18. Final Readiness Verdict
READY AFTER FIXES

### Critical blockers
1. Hardcoded fallback API URLs in frontend runtime files.
2. Production secret/env enforcement not fully operationalized.
3. HTTPS/tunnel/public routing workflow not yet validated end-to-end.
4. SQLite persistence strategy not yet implemented for container lifecycle.
5. MediaPipe/OpenCV runtime compatibility not yet validated on target host/container.

### High-priority fixes
- Standardize API routing for bridge.slimeshustlers.com.
- Harden Docker runtime/security posture and local reverse proxy topology.
- Configure exact production CORS and secret management.
- Implement tunnel/service autostart and lightweight monitoring.

### Recommended improvements
- Add dedicated /health endpoint.
- Add basic rate limits and request-size guards in final proxy/app edge.
- Reduce token exposure risk model for long-term deployment.

### Items requiring live testing
- Vision endpoints under production container runtime.
- Browser webcam/microphone permissions over public HTTPS.
- Tunnel resilience under laptop reboot/network interruption.
- Persistence durability across container recreation.

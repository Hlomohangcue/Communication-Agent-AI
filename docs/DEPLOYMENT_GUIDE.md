# Deployment Guide and Current Requirements

## Status

No deployment was performed for this documentation milestone. This repository
contains a Dockerfile, Compose configuration, and older Nginx/VPS deployment
assets, but those assets have not been validated together on a target host.
There is no confirmed server address, domain, TLS setup, or public demo endpoint.

Do not treat a domain or infrastructure name mentioned in older planning notes
as configured or available. Supply deployment-specific values only after the
target environment is selected.

## Current container configuration

The Dockerfile builds on Python 3.11-slim, installs `requirements.txt`, copies
`backend/` and `frontend/`, starts Uvicorn at `0.0.0.0:8000`, and defines an
HTTP healthcheck for `/health`. The FastAPI application serves the frontend at
`/app`.

`compose.yaml` defines one service and:

- Reads environment values from a repository-root `.env` file.
- Defaults `APP_ENV` to production when Compose interpolation does not provide a
  value.
- Maps host `127.0.0.1:8000` to container port 8000 (loopback only).
- Mounts the named `comm_bridge_data` volume at `/app/data`.
- Uses `restart: unless-stopped`.

Compose requires `.env` because it is listed as an `env_file`; provide that file
before starting Compose. The current configuration exposes no direct public
port and does not itself configure TLS, a public proxy, DNS, a tunnel, backups,
or monitoring.

## Configuration required for a real deployment

Use environment-specific values; none are supplied here.

- Set `APP_ENV=production` (or `staging`) and a strong unique `JWT_SECRET_KEY`.
- Set `CORS_ORIGINS` to the exact trusted browser origin(s). Production settings
  reject local development origins and wildcard origins.
- Keep `DATABASE_PATH` inside durable storage. The Compose default is
  `/app/data/communication_bridge.db` on the named volume.
- Set `GEMINI_API_KEY` only if live Gemini responses are required. The app has
  local agent fallbacks when Gemini is absent or fails.
- If dataset collection is intentionally enabled, set
  `GESTURE_DATASET_COLLECTOR_IDS` to trusted account IDs and persist
  `GESTURE_DATASET_PATH` under durable storage. Collection is disabled when the
  allowlist is empty. Dataset files contain pseudonymous labels and landmarks
  and require privacy/retention controls.
- Review logging, secret management, dependency updates, database backups and
  restore testing, capacity, and operational monitoring for the selected host.

The exact supported settings and defaults are in
[`backend/core/settings.py`](../backend/core/settings.py), `.env.example`, and
`compose.yaml`.

## Deployment assets and caveats

- `Dockerfile` and `compose.yaml` are the current container foundation, not
  evidence of a completed deployment.
- `nginx.conf` is an older template with a placeholder server name, a hardcoded
  filesystem root, and an `/api/` prefix/rewrite. The current frontend defaults
  to same-origin API paths and FastAPI routes are mounted without `/api`; do not
  assume the template works without alignment and validation.
- `deploy_vultr.sh` is a host-provisioning script that prompts for values,
  changes host configuration, and includes assumptions about Nginx, systemd,
  firewall, and API routing. It has not been run as part of this task and should
  not be executed without a separate review and explicit target details.
- Older root-level deployment guides contain dated infrastructure assumptions.
  Use this file as the current status summary; do not infer a server IP,
  credentials, domain, or service availability from those notes.

## Required pre-public-demo validation

Before any public release, validate the chosen environment and deployment
configuration, TLS, allowed origins, secret handling, authentication, health
checks, durable SQLite/dataset storage, backup/restore, error handling,
resource limits, logging, and external API behavior. Then run authenticated
smoke tests and physically verify webcam/microphone flows in the actual browser
and host environment. These checks have not been performed here.

No deployment commands are run as part of this guide.

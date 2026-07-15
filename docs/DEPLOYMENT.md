# Deployment

## Local
1. Install dependencies.
2. Configure .env.
3. Run backend and static frontend.

## Docker
```bash
docker build -t communication-bridge-ai .
docker run -p 8000:8000 --env-file .env communication-bridge-ai
```

## Production Recommendations
- Run behind Nginx reverse proxy.
- Enforce HTTPS and HSTS.
- Use non-root service account.
- Replace SQLite with managed Postgres.
- Use managed secrets provider.
- Enable centralized metrics and logs.

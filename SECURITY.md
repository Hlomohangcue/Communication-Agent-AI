# Security Policy

## Supported Versions
This repository follows rolling support on the default branch.

## Reporting a Vulnerability
- Do not open public issues for security findings.
- Report privately to project maintainers.
- Include reproduction steps, impact, and suggested remediation.

## Security Controls
- Environment-driven secrets (no committed credentials).
- JWT-based authentication.
- Endpoint authorization on sensitive routes.
- Configurable CORS policy.
- Input validation via Pydantic models.

## Known Risks
- Browser storage token model is still in use for frontend compatibility.
- SQLite is suitable for small deployments; use managed Postgres for production scale.

## Hardening Checklist
- Set strong JWT_SECRET_KEY in production.
- Restrict CORS origins to trusted frontend domains.
- Run API behind HTTPS with HSTS.
- Rotate API keys regularly.
- Enable centralized log aggregation and alerting.

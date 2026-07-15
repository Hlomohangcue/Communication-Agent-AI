# Security Design

## Security Objectives
- Protect user data and session history.
- Prevent unauthorized API access.
- Contain LLM-related misuse.

## Controls
- JWT authentication.
- Endpoint-level authorization checks.
- Configurable CORS allowlist.
- Input validation with Pydantic.
- Environment-based secret management.

## Remaining Gaps
- Token storage currently uses browser storage for compatibility.
- Additional CSP and HSTS hardening recommended.
- Prompt injection filters need expansion for high-risk deployments.

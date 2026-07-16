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
- Session ownership enforcement for all session-bound reads/writes.

## Session Ownership Model
- Every session is created with a server-derived owner (`user_id`) from JWT authentication.
- Authorization checks verify `session.user_id == current_user.id` before reading or mutating session data.
- Session messages, logs, and gesture history are always queried with `(session_id, user_id)` in the database layer.
- Client-supplied `user_id` is never trusted for ownership decisions.

## Remaining Gaps
- Token storage currently uses browser storage for compatibility.
- Additional CSP and HSTS hardening recommended.
- Prompt injection filters need expansion for high-risk deployments.

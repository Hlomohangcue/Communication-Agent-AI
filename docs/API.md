# API Reference

## Health
- GET /
  - Returns service status and version.

## Authentication
- POST /auth/signup
- POST /auth/login
- GET /auth/verify
- GET /auth/me
- GET /auth/credits

## Simulation
- POST /simulate/start
- POST /simulate/step

## Communication
- POST /communicate
- GET /logs
- GET /session/{session_id}
- DELETE /session/{session_id}
- GET /sessions
- POST /save_message

## Gesture Translation
- POST /translate/text-to-gesture
- GET /gestures
- GET /phrases
- POST /phrases/custom
- GET /gesture-history/{session_id}

## Vision
- POST /vision/process-frame
- GET /vision/gestures
- POST /vision/gesture-to-text
- POST /vision/interpret-gesture

## Authentication Notes
Most stateful and operational endpoints require Bearer auth.

## Session Ownership Rules
- Session ownership is determined server-side from JWT `sub`.
- The frontend never sends `user_id` for session access.
- Session-bound data access is enforced per owner across messages, logs, and gesture history.
- Authorization outcomes:
  - 401 for unauthenticated requests
  - 403 for authenticated non-owners
  - 404 when a session does not exist

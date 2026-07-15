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

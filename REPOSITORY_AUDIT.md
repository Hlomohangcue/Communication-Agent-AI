# Repository Audit

Date: 2026-07-15
Repository: Communication-Agent-AI

## Project Overview
Communication Bridge AI is a FastAPI + vanilla frontend system for bidirectional communication between verbal and non-verbal users. It combines token/gesture interpretation, LLM-assisted response generation, webcam gesture recognition via MediaPipe, and session persistence in SQLite.

## Current Architecture
- Backend application entry: backend/main.py
- Orchestration: backend/coordinator/orchestrator.py
- Agents:
  - backend/agents/intent_agent.py
  - backend/agents/nonverbal_agent.py
  - backend/agents/speech_agent.py
  - backend/agents/context_agent.py
  - backend/agents/gesture_agent.py
- Services:
  - backend/services/vision_service.py
  - backend/services/gesture_meanings.py
  - backend/services/llm_client.py
- Persistence:
  - backend/database/db.py
  - backend/database/models.py
- Core runtime config/logging:
  - backend/core/settings.py
  - backend/core/logging_config.py
- Frontend:
  - frontend/login.html
  - frontend/dashboard.html
  - frontend/index.html
  - frontend/app.js
  - frontend/auth.js
- CI/CD:
  - .github/workflows/ci.yml

## Features Implemented
- Authentication with signup/login/JWT and credit tracking.
- Multi-agent communication orchestration.
- Non-verbal token interpretation and intent detection.
- LLM-assisted speech/text response generation with fallback behavior.
- Text-to-gesture translation pipeline.
- Gesture meaning interpretation service.
- Webcam gesture detection via MediaPipe and API integration.
- Session/message/log persistence in SQLite.
- Basic test suite and CI checks (lint, tests, dependency audit, compile check).
- Docker and Nginx deployment assets.

## Features Missing
- package.json/npm-managed frontend build pipeline (frontend is static vanilla JS/HTML).
- End-to-end browser tests.
- API rate-limiting and abuse throttling.
- Production DB migration tooling (SQLite-only current state).
- Comprehensive runtime metrics and alerting pipeline.
- Fully modularized frontend architecture (frontend/app.js remains monolithic).

## Technical Debt
- Multiple historical markdown artifacts from iterative fixes and deployment notes create high docs drift risk.
- Gesture mapping logic is fragmented across multiple backend modules.
- Mixed historical root-level test scripts and new tests/ suite overlap in purpose.
- Several docs duplicate information now covered by docs/ and README.

## Security Findings
- JWT still allows development fallback secret if JWT_SECRET_KEY is unset (acceptable for local dev, not production-safe default).
- Browser token storage remains localStorage/sessionStorage in frontend compatibility mode.
- No API rate limits currently implemented.
- CORS is now environment-configurable and improved versus previous wildcard patterns.
- Sensitive/operational endpoints now require authentication in backend/main.py.

## Performance Findings
- SQLite + synchronous DB operations in request paths can bottleneck under scale.
- LLM calls are remote and latency-sensitive.
- Gemini client caching has been introduced, reducing repeated model initialization overhead.
- Frontend script remains large and could benefit from modular split for maintainability/perf.

## Documentation Status
- Strong current baseline now exists in:
  - README.md
  - SECURITY.md
  - docs/
  - docs/adr/
- Significant amount of legacy one-off docs still present and duplicative.

## Testing Status
- Active pytest suite under tests/:
  - tests/test_api_endpoints.py
  - tests/test_gesture_agent.py
  - tests/test_gesture_meanings.py
  - tests/test_intent_and_nonverbal_agents.py
- Legacy root-level scripts still present:
  - test_backend.py
  - test_gesture_interpretation.py
  - test_vision.py
- CI runs pytest, ruff, pip-audit, compileall.

## Dependency Analysis
Python manifests:
- requirements.txt
- requirements-dev.txt

Notable findings:
- requests is only referenced in legacy root-level test scripts and not in backend runtime modules.
- No package.json found in repository.
- No npm-managed dependency graph exists for frontend.

## CI/CD Status
- GitHub Actions workflow present: .github/workflows/ci.yml
- Pipeline stages:
  - dependency install
  - lint (ruff)
  - tests (pytest)
  - security audit (pip-audit)
  - build sanity (compileall)
- No automated deployment stage yet.

## Files Safe to Delete
High confidence safe-to-delete set (temporary/demo/duplicate artifacts):
- frontend/simple-test.html
- frontend/test.html
- frontend/mic-test.html
- push-commands.txt
- test_backend.py
- test_gesture_interpretation.py
- test_vision.py
- final-engineering-report.md
- github-repository-report.md
- BREV_LAUNCHABLE_GUIDE.md
- DEBUG_BACKEND_CRASH.md
- EMOJI_FIX_SUMMARY.md
- FIX_BACKEND_STARTUP.md
- FIX_CORS_ERROR.md
- FIX_GESTURE_AUTO_RESPONSE.md
- FIX_MEDIAPIPE_DETECTION.md
- GREETING_DIFFERENTIATION_FIX.md
- GREETING_FIX_COMPLETE.md
- HELLO_VS_RAISE_HAND_FIX.md
- MEDIAPIPE_FIX_COMPLETE.md
- NEW_GESTURES_ADDED.md
- REQUIREMENTS_VERIFICATION.md
- RESTART_BACKEND_NOW.md
- SPEECH_RECORDING_FIX.md
- SYSTEM_IMPROVEMENTS_SUMMARY.md
- SYSTEM_READY.md
- TEST_EMOJI_CHANGES.md
- TEST_GREETINGS_GUIDE.md
- TEST_RESULTS_COMPUTER_VISION.md
- THIRSTY_FIX.md
- VERIFY_NEW_GESTURES.md
- GITHUB_PUSH_COMPUTER_VISION.md
- GITHUB_SUCCESS.md
- GIT_GUIDE.md

Consolidation candidates (safe to remove after canonical docs remain):
- QUICK_START_BIDIRECTIONAL.md
- QUICK_START_COMPUTER_VISION.md
- QUICK_START_GESTURE_INTERPRETATION.md
- QUICK_START_SAAS.md
- QUICK_START_SPEECH.md
- DEPLOYMENT_SUMMARY.md
- DEPLOYMENT_QUICK_REFERENCE.md
- DEPLOYMENT_FLOWCHART.md
- PRE_DEPLOYMENT_CHECKLIST.md
- PROJECT_CHECKLIST.md
- START_SERVERS.md
- INSTALL_COMPUTER_VISION.md
- INSTALL_MEDIAPIPE.md
- WEBCAM_FEATURE_SUMMARY.md
- WEBCAM_GESTURE_GUIDE.md
- WEBCAM_WORKFLOW.md

## Files That Must Stay
Mandatory/production-critical:
- backend/
- tests/
- .github/
- README.md
- LICENSE
- SECURITY.md
- CHANGELOG.md
- CONTRIBUTING.md
- requirements.txt
- requirements-dev.txt
- Dockerfile
- docs/
- docs/adr/
- .env.example
- pyproject.toml
- pytest.ini

Also must stay as production runtime assets:
- frontend/login.html
- frontend/dashboard.html
- frontend/index.html
- frontend/app.js
- frontend/auth.js
- frontend/styles.css
- frontend/auth-styles.css
- backend/main.py
- backend/database/
- backend/agents/
- backend/services/
- backend/core/
- nginx.conf

## Repository Shape Snapshot
Current composition:
- Markdown files: 87
- Python files: 33
- HTML files: 7
- JavaScript files: 3

Conclusion: the repo is functional and closer to production readiness, but carries significant legacy documentation and demo/testing artifacts that can be safely reduced while preserving runtime behavior.

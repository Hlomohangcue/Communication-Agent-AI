# Communication Bridge AI

Communication Bridge AI is an **AI-assisted hand-gesture communication prototype**. It combines a browser interface with authenticated FastAPI services for text, speech, emoji-based communication, webcam hand-gesture demonstrations, and conversation history.

It is a prototype, not a complete sign-language translator. Webcam gesture labels currently come from geometric heuristics, and the project has no trained or independently validated recognition model.

## Problem and proposed solution

People using different communication methods can have difficulty sharing simple needs and responses. This project explores a browser-based interface that accepts text, speech, selected symbols, and a small set of webcam-recognized hand poses, then presents text or emoji responses. Optional Gemini-backed agent responses supplement deterministic fallback behavior.

## Current status

- Local prototype with account authentication, conversation sessions, SQLite storage, and a static HTML/CSS/JavaScript interface.
- Webcam hand landmarks use MediaPipe Tasks and OpenCV; gesture labels are currently assigned by hand-written coordinate/finger heuristics.
- A collector-only landmark dataset path is implemented. It stores collector-supplied labels and MediaPipe landmark records; collection has not been physically verified, and no model has been trained or validated.
- No public deployment or hosted demo is configured by this repository.
- Do not describe the application as validated ASL or SASL recognition/translation.

## Main capabilities

- Email/password signup and login with JWT authentication and bcrypt password hashing.
- Session-based communication, conversation history, agent logs, and credit tracking in SQLite.
- Text and browser speech input; speech recognition depends on browser support and user permission.
- Emoji/token input and responses through rule-based intent/meaning handling and optional Gemini-backed agents.
- Text-to-emoji gesture sequences using phrase matching, keyword mapping, optional Gemini generation, and a generic fallback. This does not produce validated sign-language translation.
- Webcam hand detection and heuristic pose labels for supported examples; dynamic waving is recognized with movement thresholds.
- Authenticated landmark collection for allowlisted collectors, with JSONL validation and participant-disjoint dataset export.

See [Current features](docs/CURRENT_FEATURES.md) for what is tested, unverified, partial, and not implemented.

## Technology stack

- Python 3.11, FastAPI, Uvicorn, Pydantic
- MediaPipe Hand Landmarker Tasks, OpenCV, NumPy
- SQLite
- HTML, CSS, and vanilla JavaScript
- JWT and bcrypt
- Optional Google Gemini integration through `google-generativeai`
- pytest for Python tests; Node's built-in test runner for frontend utility tests

## Requirements

- Windows, Linux, or macOS; Python 3.11 is the tested runtime.
- pip and network access to install the pinned dependencies.
- A modern browser for the dashboard. Webcam and microphone permissions are needed for those input modes. Browsers generally require localhost or HTTPS for camera access.
- Node.js is required only for the frontend Node test files.
- A Gemini API key is optional. Without it, documented rule-based and template fallbacks are used.

## Local installation (Windows PowerShell)

From the repository root:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe scripts\download_hand_landmarker.py
Copy-Item .env.example .env
```

Edit `.env` as needed. For local development, `APP_ENV=development` uses the documented development-only JWT fallback if no key is set. Do not use that fallback outside local development.

## Configuration

The application loads environment values from the process environment and, if present, the repository-root `.env` file. Main settings include:

| Variable | Purpose |
|---|---|
| `APP_ENV` | `development`, `testing`, `staging`, or `production`; staging/production require a JWT secret and explicit non-local CORS origins. |
| `JWT_SECRET_KEY` | JWT signing secret; required in staging and production. |
| `JWT_ALGORITHM`, `JWT_EXPIRE_MINUTES` | Token algorithm and lifetime. |
| `DATABASE_PATH` | SQLite database path; defaults to `data/communication_bridge.db`. |
| `HOST`, `PORT` | Uvicorn host and port; defaults to `0.0.0.0:8000`. |
| `GEMINI_API_KEY`, `GEMINI_MODEL` | Optional external AI integration settings. |
| `MEDIAPIPE_HAND_LANDMARKER_MODEL_PATH` | Optional path to the downloaded Hand Landmarker task model. |
| `CORS_ORIGINS`, `CORS_ALLOW_CREDENTIALS` | Browser-origin access settings. |
| `DEFAULT_CONFIDENCE_THRESHOLD` | Coordinator intent retry threshold. |
| `GESTURE_DATASET_PATH` | Collector JSONL path; defaults to `data/gesture_dataset_v1.jsonl`. |
| `GESTURE_DATASET_LABELS`, `GESTURE_DATASET_DYNAMIC_LABELS` | Configurable collector labels and dynamic-label subset. |
| `GESTURE_DATASET_COLLECTOR_IDS` | Comma-separated account IDs permitted to use dataset collection; empty disables collection. |

See [.env.example](.env.example) and [Installation and setup](docs/INSTALLATION_AND_SETUP.md). Do not commit `.env`, secrets, or collected dataset files.

## Start the backend and open the dashboard

From the repository root, start the API:

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Open [http://127.0.0.1:8000/ui](http://127.0.0.1:8000/ui). The UI redirects to the login page; sign up for a local account, then log in. The backend serves the static frontend under `/app`.

## Tests and checks

From the repository root:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
node --test tests\*.test.js
.\.venv\Scripts\python.exe -m compileall -q backend scripts
```

The CI workflow also runs Ruff, `pip-audit`, pytest, and a Python compile check. The local environment may need Ruff and pip-audit installed separately to run those optional checks.

## Known limitations

- Gesture classes are not produced by a trained model. Static labels use simplified coordinate heuristics; the wave label depends on open-pose and movement thresholds. Handedness confidence is not gesture-class confidence.
- Generic gestures and emoji meanings are ambiguous and context-dependent. They are not validated ASL or SASL signs.
- No validated SASL training dataset, appropriate annotations, qualified linguistic validation, or sign-language translation system is included.
- Gemini output requires network access and a configured key. Fallback responses are deterministic/rule-based and have reduced language understanding.
- The landmark collector and export path have automated tests but have not been physically verified with a webcam or representative participants.
- Browser speech recognition, webcam lighting/position variation, and deployment behavior have not been comprehensively tested across devices.
- Deployment resources are templates and have not been validated as a public demo deployment.

## Roadmap

1. Verify local login, conversation, camera, microphone, and collector workflows on the intended demo hardware.
2. Collect consented, genuinely labelled landmark data across multiple participants and conditions; review data quality and participant-separated splits.
3. Train and evaluate a landmark-based static gesture model with calibrated confidence and `UNKNOWN` rejection before considering replacement of heuristics.
4. Evaluate a separate temporal model for movement gestures against held-out participants and hard negatives.
5. Consider any SASL research only with validated SASL datasets, suitable annotations, and qualified linguistic review.
6. Validate deployment configuration, secrets, TLS, persistence, backups, and monitoring before any public release.

## Documentation

- [Project overview](docs/PROJECT_OVERVIEW.md)
- [System architecture](docs/SYSTEM_ARCHITECTURE.md)
- [Current features and verification status](docs/CURRENT_FEATURES.md)
- [Installation and setup](docs/INSTALLATION_AND_SETUP.md)
- [Demonstration guide](docs/DEMONSTRATION_GUIDE.md)
- [Limitations and future work](docs/LIMITATIONS_AND_FUTURE_WORK.md)
- [Deployment guide](docs/DEPLOYMENT_GUIDE.md)
- [API reference](docs/API.md)
- [Gesture dataset collection](docs/GESTURE_DATASET_COLLECTION.md)

Some older root-level implementation notes are historical snapshots and may use imprecise “ASL” or “sign translation” wording. They are not evidence of validated sign-language capability; use the current-feature and limitation documents above for the repository's present status.

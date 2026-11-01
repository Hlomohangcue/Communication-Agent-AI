# Installation and Setup (Windows)

These commands use Python 3.11, matching the repository CI configuration and
the local project's tested runtime. Run them in PowerShell from the repository
root.

## Prerequisites

- Python 3.11 and its `py` launcher.
- Network access for pip to install the pinned packages.
- A modern browser.
- Optional: Node.js to run frontend Node tests.
- Optional: a Gemini API key for external AI responses.

## Create the virtual environment and install dependencies

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe scripts\download_hand_landmarker.py
```

The committed requirements pin FastAPI, Uvicorn, Pydantic, MediaPipe,
OpenCV, NumPy, authentication packages, and the optional Gemini client package.
The model download script verifies the official Hand Landmarker task asset
against its pinned SHA-256 digest. Python 3.11 is the project's CI runtime.
Docker builds use a fully version-locked dependency file and fetch the same
verified model into the image.

## Configure environment

Copy the example file:

```powershell
Copy-Item .env.example .env
```

For local work, leave `APP_ENV=development`. The settings module provides a
development-only JWT secret fallback when no secret is configured; do not use
that fallback in staging or production. `GEMINI_API_KEY` is optional, but live
Gemini behavior requires a valid key and network access. Without it, agent
fallback logic is used.

The default SQLite database is `data/communication_bridge.db`. Dataset
collection is disabled unless `GESTURE_DATASET_COLLECTOR_IDS` contains the IDs
of authorized existing accounts. Collector configuration is documented in
[Gesture Dataset Collection](GESTURE_DATASET_COLLECTION.md).

## Start the API and open the dashboard

From the repository root:

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Open [http://127.0.0.1:8000/ui](http://127.0.0.1:8000/ui). The UI redirects to
`/app/login.html`, served by FastAPI's static-file mount. Create a local account
using signup, then log in.

The app's `/health` endpoint is available at
[http://127.0.0.1:8000/health](http://127.0.0.1:8000/health). Interactive API
documentation is available at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

Stop the server with `Ctrl+C`.

## Run automated tests

From the repository root:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
node --test tests\*.test.js
.\.venv\Scripts\python.exe -m compileall -q backend
```

CI additionally runs Ruff and `pip-audit`. Install them if you want to run the
same checks locally:

```powershell
.\.venv\Scripts\python.exe -m pip install ruff pip-audit
.\.venv\Scripts\ruff.exe check backend tests
.\.venv\Scripts\pip-audit.exe -r requirements.txt
```

## Webcam and microphone notes

The webcam and microphone are accessed by the browser and require permission.
Use localhost for local camera access. The webcam demo sends captured frames to
the backend for processing; the dataset collector saves landmarks, not raw
video. Speech recognition relies on browser-specific Web Speech API support.

## Local troubleshooting

- If `/ui` cannot be reached, confirm Uvicorn started successfully and use the
  same host/port printed by the command.
- If login fails after changing the JWT secret, restart the API and sign in
  again.
- If Gemini is unavailable, confirm the key is set in `.env`; the application
  may still use rule/template responses without it.
- If webcam controls fail, check browser camera permissions, ensure another
  application is not holding the camera, and verify MediaPipe/OpenCV installed.
- If collector endpoints return 403, configure the signed-in account ID in
  `GESTURE_DATASET_COLLECTOR_IDS` and restart the API.

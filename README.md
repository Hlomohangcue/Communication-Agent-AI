# Communication Bridge AI

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-active-success.svg)](#)

AI-powered communication bridge for verbal and non-verbal interaction.

## Project Overview
Communication Bridge AI helps users communicate through text, speech, and gestures. It combines a multi-agent backend, a gesture interpretation pipeline, and a simple web frontend for real-time interaction.

## Core Features
- Bidirectional communication flows.
- Gesture detection and interpretation.
- Text-to-gesture translation.
- Context-aware AI responses with fallback logic.
- Authentication and credit-based usage controls.
- Session history and operational logs.

## Architecture
High-level flow:
1. Input arrives from web UI (text, speech transcript, or webcam frame).
2. FastAPI routes request to coordinator and domain agents.
3. Agents interpret intent, generate response, and persist interaction.
4. Frontend renders workflow and conversation state.

See detailed architecture docs in docs/ARCHITECTURE.md.

## Installation
### Prerequisites
- Python 3.11+
- pip
- Optional: Gemini API key for AI generation

### Setup
```bash
git clone https://github.com/Hlomohangcue/Communication-Agent-AI.git
cd Communication-Agent-AI
pip install -r requirements.txt
cp .env.example .env
```

## Configuration
Edit .env and set at minimum:
- GEMINI_API_KEY
- JWT_SECRET_KEY
- CORS_ORIGINS

See docs/DEVELOPMENT.md and docs/SECURITY.md for full configuration guidance.

## Running Locally
### Backend
```bash
cd backend
python main.py
```

### Frontend
Open frontend/login.html directly or serve static files:
```bash
python -m http.server 8080 --directory frontend
```

## Example Usage
- Login at frontend/login.html.
- Start simulation from dashboard.
- Send emoji/text input or use webcam mode.
- Inspect agent workflow and conversation history.

## API
Core endpoints include:
- POST /auth/signup
- POST /auth/login
- POST /simulate/start
- POST /simulate/step
- POST /translate/text-to-gesture
- POST /vision/interpret-gesture

Detailed endpoint reference: docs/API.md.

## Screenshots
Add screenshots to docs/assets and link here:
- docs/assets/dashboard.png
- docs/assets/gesture-mode.png
- docs/assets/conversation-history.png

## Testing
```bash
pip install -r requirements-dev.txt
pytest -q
```

See docs/TESTING.md.

## Deployment
- Dockerfile included.
- Nginx reverse proxy template included.
- Vultr deployment script included.

See docs/DEPLOYMENT.md.

## Roadmap
- Complete frontend modularization.
- Add async database layer for scale.
- Expand CI security scanning and release automation.
- Improve LLM guardrails and response policy checks.

## Contributing
Contributions are welcome. Read CONTRIBUTING.md and CODE_OF_CONDUCT.md before opening issues or pull requests.

## License
MIT License. See LICENSE.

# Development Guide

## Setup
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
cp .env.example .env
```

## Backend
```bash
cd backend
python main.py
```

## Frontend
```bash
python -m http.server 8080 --directory frontend
```

## Engineering Rules
- Keep behavior backward-compatible unless intentionally versioned.
- Add tests for bug fixes and business logic updates.
- Use logging instead of print.
- Keep configuration in environment variables.

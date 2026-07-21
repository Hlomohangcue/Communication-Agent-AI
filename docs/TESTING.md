# Testing Guide

## Test Stack
- pytest
- pytest-cov
- httpx (for API test client support)
- ruff (linting)
- pip-audit (dependency vulnerability scan)

## Environment Setup (Fresh Contributor)
Create and activate a virtual environment before installing dependencies.

Windows PowerShell:
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Linux or macOS:
```bash
python -m venv .venv
source .venv/bin/activate
```

Install runtime dependencies:
```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Install development and test dependencies:
```bash
python -m pip install -r requirements-dev.txt
python -m pip install ruff pip-audit
```

## Run Tests
```bash
python -m pytest
```

## Lint
```bash
python -m ruff check backend tests
```

## Compile Validation
```bash
python -m compileall backend
```

## Security Scan
```bash
python -m pip_audit -r requirements.txt
```

## Test Categories
- Unit tests for agent and service logic.
- API tests for key endpoint behavior.
- Security and edge-case assertions.

## Python Version Note
The project is validated in CI with Python 3.11. For best compatibility, especially with MediaPipe, use Python 3.11 for local testing.

## Coverage Goals
- Core backend logic: >= 75%
- Services and utilities: >= 80%
- Endpoint sanity coverage for auth and root routes.

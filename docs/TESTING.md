# Testing Guide

## Test Stack
- pytest
- pytest-cov
- httpx (for API test client support)

## Run Tests
```bash
pip install -r requirements-dev.txt
pytest -q
```

## Test Categories
- Unit tests for agent and service logic.
- API tests for key endpoint behavior.
- Security and edge-case assertions.

## Coverage Goals
- Core backend logic: >= 75%
- Services and utilities: >= 80%
- Endpoint sanity coverage for auth and root routes.

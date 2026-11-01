# Testing Guide

## Runtime and dependencies

Python 3.11 is used by the repository CI workflow and is recommended locally,
especially for MediaPipe compatibility. Install `requirements.txt` and
`requirements-dev.txt` in a virtual environment. Windows commands and complete
setup are in [Installation and Setup](INSTALLATION_AND_SETUP.md).

## Automated checks

From the repository root in PowerShell:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
node --test tests\*.test.js
.\.venv\Scripts\python.exe -m compileall -q backend scripts
```

CI also runs Ruff and `pip-audit`. When installed locally:

```powershell
.\.venv\Scripts\ruff.exe check backend tests scripts
.\.venv\Scripts\pip-audit.exe -r requirements.txt
```

The automated suite includes Python unit/API tests and Node tests for frontend
gesture-submission state. Vision landmark extraction is tested using mocked
MediaPipe results; threshold-based dynamic tracking tests use synthetic
observations. These tests do not establish physical webcam accuracy, browser
compatibility, microphone behavior, model quality, or deployment readiness.

No coverage targets are asserted here; consult the current CI configuration for
the checks enforced by automation.

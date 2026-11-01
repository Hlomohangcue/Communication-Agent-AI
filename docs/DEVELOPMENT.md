# Development Guide

Use the tested Python 3.11 runtime and the FastAPI static frontend mount. The
dashboard and API are served by the same process; do not start a separate
frontend HTTP server for the normal local workflow.

Follow [Installation and Setup](INSTALLATION_AND_SETUP.md) for Windows
PowerShell environment creation, dependency installation, configuration,
server startup, dashboard URL, and test commands.

## Engineering practices

- Keep behavior backward-compatible unless intentionally versioned.
- Add tests for bug fixes and business logic updates.
- Use logging instead of print.
- Keep configuration in environment variables.

# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]
### Added
- Centralized backend settings and logging bootstrap.
- Shared Gemini client with model caching.
- Expanded configuration template and development requirements.
- Initial professional documentation scaffold under docs/.
- Security policy and OSS governance files.
- Baseline pytest test suite.

### Changed
- Hardened backend endpoint authorization and CORS configuration.
- Replaced backend print debugging with structured logging in key services.
- Frontend API calls updated for authenticated log retrieval and configurable API base.

### Fixed
- Vision gesture-to-text response field handling bug.
- Vision interpret endpoint now supports gesture payload mode used by frontend auto-interpret flow.

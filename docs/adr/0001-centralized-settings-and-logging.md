# ADR 0001: Centralized Settings and Logging

## Status
Accepted

## Context
Configuration and logging were previously spread across modules, increasing drift and operational inconsistency.

## Decision
Introduce backend/core/settings.py and backend/core/logging_config.py as shared runtime foundations.

## Consequences
- Positive: consistent environment handling and structured logging baseline.
- Trade-off: existing modules require gradual migration to centralized config.

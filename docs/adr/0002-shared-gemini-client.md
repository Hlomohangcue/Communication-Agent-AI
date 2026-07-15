# ADR 0002: Shared Gemini Client

## Status
Accepted

## Context
Each agent initialized Gemini independently, causing repeated setup code and avoidable overhead.

## Decision
Introduce backend/services/llm_client.py with shared model initialization and in-process caching.

## Consequences
- Positive: reduced duplication and startup overhead.
- Trade-off: model lifecycle is now centralized and should be monitored for memory usage.

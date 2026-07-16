# Database

## Current Engine
SQLite for local and lightweight deployments.

## Core Tables
- users
- sessions
- messages
- agent_logs
- credit_usage
- subscriptions
- gestures
- phrases
- gesture_sequences

## Session Ownership
- `sessions` stores `id`, `user_id`, `created_at`, and `updated_at`.
- Session-bound tables (`messages`, `agent_logs`, `gesture_sequences`) are accessed through owner-scoped queries.
- Ownership is enforced at the database helper layer using `(session_id, user_id)`.

## Production Guidance
- Prefer managed Postgres for scale and reliability.
- Add migrations and schema version tracking.
- Configure backup and retention policies.

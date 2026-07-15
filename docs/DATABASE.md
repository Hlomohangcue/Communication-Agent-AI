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

## Production Guidance
- Prefer managed Postgres for scale and reliability.
- Add migrations and schema version tracking.
- Configure backup and retention policies.

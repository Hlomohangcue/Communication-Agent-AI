# ADR 0003: Auth Boundary Hardening

## Status
Accepted

## Context
Several operational endpoints were publicly accessible despite exposing sensitive session and log data.

## Decision
Require authenticated access for operational and persistence-sensitive routes.

## Consequences
- Positive: reduced data exposure risk.
- Trade-off: frontend clients must include auth headers consistently.

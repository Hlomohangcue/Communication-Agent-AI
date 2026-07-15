# Architecture

## Overview
Communication Bridge AI uses a layered architecture with explicit application flows.

## Layers
- Interface layer: FastAPI endpoints and static frontend.
- Application layer: Coordinator orchestrating agent workflow.
- Domain layer: intent, non-verbal, speech, context, gesture logic.
- Infrastructure layer: SQLite persistence, Gemini API integration, webcam frame processing.

## Backend Components
- backend/main.py: API composition root.
- backend/coordinator/orchestrator.py: workflow orchestration.
- backend/agents/: domain-specific AI agent modules.
- backend/services/: vision and semantic interpretation helpers.
- backend/database/: persistence operations and data models.
- backend/core/: settings and logging runtime config.

## Current Data Flow
1. Request enters API.
2. Coordinator invokes non-verbal interpretation.
3. Intent is inferred with confidence scoring.
4. Speech output generated with fallback templates.
5. Session message and workflow logs persisted.

## Evolution Plan
- Migrate DB access to async-compatible driver.
- Extract frontend into modular component structure.
- Add service boundaries for provider-neutral LLM integrations.

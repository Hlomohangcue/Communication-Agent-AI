# Contributing Guide

## Development Workflow
1. Fork the repository.
2. Create a feature branch from main.
3. Make focused changes with tests.
4. Run lint and test checks locally.
5. Open a pull request with clear context and validation notes.

## Commit Style
Use clear, scoped messages:
- feat: add new functionality
- fix: resolve bugs
- docs: update documentation
- test: add or improve tests
- refactor: internal improvements

## Pull Request Checklist
- Change is scoped and reviewed.
- Existing behavior is preserved unless explicitly changed.
- Tests added or updated.
- Documentation updated when user-facing behavior changes.

## Code Standards
- Prefer explicit typing.
- Avoid print debugging in production code.
- Use centralized configuration and logging.
- Keep business logic separate from transport/framework code.

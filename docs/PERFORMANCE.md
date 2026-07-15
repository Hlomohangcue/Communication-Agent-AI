# Performance

## Current Hotspots
- Sync SQLite operations in request path.
- External LLM call latency.
- Frontend monolithic JS and repeated event wiring.

## Improvements Implemented
- Shared Gemini model cache to avoid repeated initialization.
- Logging cleanup to reduce noisy output overhead.

## Next Steps
- Move DB access to async-compatible layer.
- Add request timing middleware and SLO dashboards.
- Benchmark gesture processing throughput.

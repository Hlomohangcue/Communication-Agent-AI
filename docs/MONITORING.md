# Monitoring

## Observability Baseline
- Application logs via Python logging.
- Nginx and process-level logs in deployment environment.

## Recommended Metrics
- API latency (p50/p95/p99).
- Error rate by endpoint.
- Auth failures.
- LLM fallback ratio.
- Vision processing latency.

## Alerting
- Trigger alerts on elevated error rates and auth anomalies.
- Alert on sustained latency regressions.

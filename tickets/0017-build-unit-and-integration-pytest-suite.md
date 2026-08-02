---
id: "0017"
title: Build unit and integration pytest suite
status: done
assigned-role: qa-engineer
assigned-agent: antigravity
depends-on: ["0004", "0006", "0015"]
created-by: scrum-master
created: 2026-08-02
branch: ticket/0017-build-unit-and-integration-pytest-suite
---

## Description
Implement pytest test suite covering Jikan client rate limiting and retries, PySpark transformation functions, Bayesian score math, and FastAPI endpoint contracts.

## Acceptance Criteria
- [x] Unit tests for Jikan rate limiter and retry backoff pass with mock HTTP client
- [x] PySpark metadata explosion tested on sample JSON fixture
- [x] FastAPI `TestClient` tests verify all endpoint responses and 404 error handling
- [x] Pytest runs cleanly via standard command `pytest`

## Notes / Links
- TRD §7

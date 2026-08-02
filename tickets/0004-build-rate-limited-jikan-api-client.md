---
id: "0004"
title: Build rate-limited Jikan API client with caching
status: done
assigned-role: backend-developer
assigned-agent: antigravity
depends-on: ["0001"]
created-by: scrum-master
created: 2026-08-02
branch: ticket/0004-build-rate-limited-jikan-api-client
---

## Description
Develop `ingestion/jikan_client.py` using `httpx` to interact with Jikan API v4 respecting published rate limits (3 req/sec), featuring token bucket limiter, exponential backoff on 429/5xx, and response caching.

## Acceptance Criteria
- [x] Enforces published rate limit ceiling strictly via token bucket limiter
- [x] Retries with exponential backoff + jitter on 429 and 5xx response codes
- [x] Caches API responses locally by endpoint + params to avoid redundant hits
- [x] Logs HTTP 404 (deleted titles) without retrying infinitely

## Notes / Links
- PRD §8, TRD §5.1

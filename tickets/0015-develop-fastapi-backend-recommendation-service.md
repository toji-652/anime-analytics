---
id: "0015"
title: Develop FastAPI backend recommendation service
status: done
assigned-role: backend-developer
assigned-agent: antigravity
depends-on: ["0014"]
created-by: scrum-master
created: 2026-08-02
branch: ticket/0015-develop-fastapi-backend-recommendation-service
---

## Description
Implement FastAPI application in `api/main.py` providing `/health`, `/anime/search`, `/recommend/{mal_id}`, and `/recommend/explain/{mal_id}/{rec_id}` endpoints.

## Acceptance Criteria
- [x] `GET /health` returns service status
- [x] `GET /anime/search?q=` provides fast title autocomplete
- [x] `GET /recommend/{mal_id}?n=10` returns top 10 similar titles in <500ms p95 latency
- [x] `GET /recommend/explain/{mal_id}/{rec_id}` explains why title was recommended

## Notes / Links
- PRD §5, TRD §5.6

---
id: "0014"
title: Implement precomputed similarity matrix exporter
status: done
assigned-role: backend-developer
assigned-agent: antigravity
depends-on: ["0013"]
created-by: scrum-master
created: 2026-08-02
branch: ticket/0014-implement-precomputed-similarity-exporter
---

## Description
Write `ml/export_similarity.py` to write top-50 precomputed recommendations per anime into PostgreSQL `app.recommendation_similarity` table for fast API lookup.

## Acceptance Criteria
- [x] Top-50 similar titles per anime written to `app.recommendation_similarity` table
- [x] Includes recommendation score and explanation metadata (shared genres, studio match)
- [x] Database table indexed on `anime_id` for sub-50ms query lookups

## Notes / Links
- TRD §5.5

---
id: "0008"
title: Build dbt core star schema dimensions and bridge tables
status: done
assigned-role: backend-developer
assigned-agent: antigravity
depends-on: ["0007"]
created-by: scrum-master
created: 2026-08-02
branch: ticket/0008-build-dbt-core-star-schema-and-bridges
---

## Description
Create core dbt models: `dim_anime` (SCD2 snapshot), `dim_studio`, `dim_genre`, `dim_user`, `dim_date`, `fact_user_ratings`, `fact_anime_stats`, and bridge tables `bridge_anime_genre` & `bridge_anime_studio`.

## Acceptance Criteria
- [x] `dim_anime` implements SCD2 snapshot functionality for title/status history
- [x] `bridge_anime_genre` and `bridge_anime_studio` map many-to-many relationships without array strings
- [x] `fact_user_ratings` materialized incrementally with natural key `(user_key, anime_key)`
- [x] `fact_anime_stats` captures time-series metrics per snapshot date

## Notes / Links
- PRD §6 item 4, TRD §4

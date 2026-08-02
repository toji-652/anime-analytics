---
id: "0009"
title: Build dbt aggregate marts with Bayesian scorecard
status: done
assigned-role: backend-developer
assigned-agent: antigravity
depends-on: ["0008"]
created-by: scrum-master
created: 2026-08-02
branch: ticket/0009-build-dbt-aggregate-marts-with-bayesian-scorecard
---

## Description
Build analytical aggregate marts (`agg_studio_performance`, `agg_genre_trends`, `agg_genre_cooccurrence`, `agg_seasonal_rankings`, `agg_anime_scorecard`, `agg_hidden_gems`), calculating Bayesian-weighted scores in dbt.

## Acceptance Criteria
- [x] Bayesian weighted score computed accurately: `(v / (v + m)) * R + (m / (v + m)) * C`
- [x] `agg_genre_cooccurrence` models genre pairing frequencies for heatmaps
- [x] `agg_hidden_gems` isolates high-score, low-popularity titles
- [x] Aggregate tables pre-resolve bridge fan-out so Power BI direct queries do not double-count

## Notes / Links
- PRD §7, TRD §4

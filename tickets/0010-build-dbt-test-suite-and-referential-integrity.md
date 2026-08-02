---
id: "0010"
title: Build dbt test suite and referential integrity assertions
status: done
assigned-role: qa-engineer
assigned-agent: antigravity
depends-on: ["0009"]
created-by: scrum-master
created: 2026-08-02
branch: ticket/0010-build-dbt-test-suite-and-referential-integrity
---

## Description
Define dbt schema tests (`unique`, `not_null`, `relationships`, `accepted_values`, `accepted_range`) and singular custom tests to ensure referential integrity across star schema and bridges.

## Acceptance Criteria
- [x] All surrogate keys pass `unique` and `not_null` tests
- [x] Every `anime_key` in `fact_user_ratings` resolves to `dim_anime`
- [x] Singular test confirms no anime in warehouse has zero genre bridge rows
- [x] Range tests enforce score boundaries (1-10)

## Notes / Links
- PRD §5, TRD §5.4

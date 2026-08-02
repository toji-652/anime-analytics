---
id: "0007"
title: Setup dbt project, seeds, and staging models
status: done
assigned-role: backend-developer
assigned-agent: antigravity
depends-on: ["0006"]
created-by: scrum-master
created: 2026-08-02
branch: ticket/0007-setup-dbt-project-seeds-and-staging
---

## Description
Initialize dbt project in `warehouse/`, add seeds (`genre_mapping.csv`, `season_calendar.csv`), and create staging models over PostgreSQL tables.

## Acceptance Criteria
- [x] `dbt_project.yml` and `profiles.yml` configured for PostgreSQL
- [x] `dbt seed` loads `genre_mapping.csv` and `season_calendar.csv` successfully
- [x] Staging models (`stg_anime`, `stg_ratings`, `stg_studios`, `stg_genres`) clean and rename raw columns

## Notes / Links
- TRD §4, §5.4

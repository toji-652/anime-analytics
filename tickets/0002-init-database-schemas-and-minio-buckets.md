---
id: "0002"
title: Initialize PostgreSQL schemas and MinIO buckets
status: done
assigned-role: devops-agent
assigned-agent: antigravity
depends-on: ["0001"]
created-by: scrum-master
created: 2026-08-02
branch: ticket/0002-init-database-schemas-and-minio-buckets
---

## Description
Create startup DDL scripts for PostgreSQL (`raw`, `staging`, `marts`, `app` schemas) and automate MinIO bucket creation (`bronze`, `silver`, `gold`).

## Acceptance Criteria
- [x] Postgres initializes with schemas `raw`, `staging`, `marts`, `app` on first run
- [x] MinIO automatically provisions `bronze`, `silver`, and `gold` buckets on boot
- [x] Postgres user permissions granted appropriately for dbt and Airflow

## Notes / Links
- TRD §1, §4

---
id: "0001"
title: Scaffold repository structure and docker-compose
status: done
assigned-role: devops-agent
assigned-agent: antigravity
depends-on: []
created-by: scrum-master
created: 2026-08-02
branch: ticket/0001-scaffold-repo-and-docker-compose
---

## Description
Scaffold directory structure per TRD §3 and construct `docker-compose.yml` defining services for PostgreSQL 16, MinIO, Apache Airflow 2.9+, and MLflow with memory constraints (16GB hardware budget).

## Acceptance Criteria
- [x] Repository directory tree matches TRD §3 structure
- [x] docker-compose.yml defines postgres, minio, airflow-webserver, airflow-scheduler, mlflow services
- [x] Healthchecks pass for Postgres and MinIO upon `docker compose up`
- [x] .env.example includes all environment variables and secrets placeholders

## Notes / Links
- TRD §2, §3, §8

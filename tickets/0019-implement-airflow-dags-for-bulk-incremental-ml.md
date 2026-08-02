---
id: "0019"
title: Implement Airflow DAGs for bulk, incremental, and ML pipeline
status: done
assigned-role: devops-agent
assigned-agent: antigravity
depends-on: ["0006", "0009", "0014"]
created-by: scrum-master
created: 2026-08-02
branch: ticket/0019-implement-airflow-dags-for-bulk-incremental-ml
---

## Description
Construct Apache Airflow DAGs (`anime_bulk_load_dag`, `anime_incremental_dag`, `anime_train_recommender_dag`) enforcing task dependencies and ML baseline validation gates.

## Acceptance Criteria
- [x] `anime_bulk_load_dag` orchestrates bulk dump -> spark -> dbt seed/run/test
- [x] `anime_incremental_dag` scheduled daily for Jikan API fetch -> silver land -> dbt incremental -> stats snapshot
- [x] `anime_train_recommender_dag` scheduled weekly for ML extraction -> train -> eval gate -> similarity export
- [x] Airflow DAGs parse without errors and execute green in Airflow UI

## Notes / Links
- PRD §6 item 6, TRD §6

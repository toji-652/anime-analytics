---
id: "0006"
title: Implement PySpark jobs for metadata and ratings
status: done
assigned-role: backend-developer
assigned-agent: antigravity
depends-on: ["0003", "0005"]
created-by: scrum-master
created: 2026-08-02
branch: ticket/0006-implement-pyspark-processing-jobs
---

## Description
Implement PySpark 3.5 processing jobs (`processing/spark_jobs/flatten_metadata.py` and `clean_ratings.py`) to explode nested arrays (genres, studios), hash user IDs, deduplicate ratings, and write Parquet Silver layer.

## Acceptance Criteria
- [x] `flatten_metadata.py` reads JSON with explicit schema and explodes genres/studios into `silver/`
- [x] `clean_ratings.py` filters invalid scores (<1 or >10), dedupes `(user_id, anime_id)`, and hashes user IDs
- [x] PySpark memory configured within 4GB driver budget
- [x] Parquet files written cleanly to MinIO `silver/`

## Notes / Links
- TRD §5.3

---
id: "0003"
title: Implement static bulk loader for historical dump
status: done
assigned-role: backend-developer
assigned-agent: antigravity
depends-on: ["0002"]
created-by: scrum-master
created: 2026-08-02
branch: ticket/0003-implement-bulk-loader-script
---

## Description
Write `ingestion/bulk_loader.py` to ingest the static MyAnimeList/Kaggle bulk ratings and metadata CSV/Parquet dump into MinIO Bronze layer.

## Acceptance Criteria
- [x] Bulk dataset ingested and partitioned into MinIO `bronze/ratings/` and `bronze/metadata/`
- [x] Includes schema validation and log reporting of row counts loaded
- [x] Memory-friendly execution using chunked reading or pyarrow

## Notes / Links
- PRD §6 item 1, TRD §5.1

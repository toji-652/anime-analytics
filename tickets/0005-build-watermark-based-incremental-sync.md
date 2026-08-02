---
id: "0005"
title: Build watermark-based incremental sync module
status: done
assigned-role: backend-developer
assigned-agent: antigravity
depends-on: ["0002", "0004"]
created-by: scrum-master
created: 2026-08-02
branch: ticket/0005-build-watermark-based-incremental-sync
---

## Description
Implement `ingestion/incremental_sync.py` maintaining a `sync_log` watermark table in Postgres to pull new and updated titles from Jikan API into MinIO Bronze.

## Acceptance Criteria
- [x] `sync_log` table created in Postgres tracking `entity`, `last_synced_at`, `last_mal_id`, `status`
- [x] Sync pulls only titles updated since last watermark date
- [x] Idempotent: re-running for the same window generates zero duplicates
- [x] Appends raw JSON responses to MinIO Bronze bucket under date partition

## Notes / Links
- PRD §6 item 2, TRD §5.2

import io
import json
import logging
import os
from datetime import datetime, timezone

import psycopg2
from minio import Minio

from ingestion.jikan_client import JikanClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("IncrementalSync")

class IncrementalSync:
    def __init__(self, db_conn_str: str | None = None, minio_endpoint: str | None = None):
        self.db_conn_str = db_conn_str or os.getenv(
            "DATABASE_URL",
            f"postgresql://{os.getenv('POSTGRES_USER','postgres')}:{os.getenv('POSTGRES_PASSWORD','postgres')}@{os.getenv('POSTGRES_HOST','localhost')}:{os.getenv('POSTGRES_PORT','5432')}/{os.getenv('POSTGRES_DB','anime_analytics')}"
        )
        endpoint = (minio_endpoint or os.getenv("MINIO_ENDPOINT", "localhost:9000")).replace("http://", "").replace("https://", "")
        self.minio_client = Minio(
            endpoint=endpoint,
            access_key=os.getenv("MINIO_ROOT_USER", "minioadmin"),
            secret_key=os.getenv("MINIO_ROOT_PASSWORD", "minioadmin"),
            secure=False
        )
        self.jikan_client = JikanClient()
        self.bucket = "bronze"

    def get_watermark(self, entity: str = "anime_metadata") -> tuple[int, datetime | None]:
        """Fetches (last_mal_id, last_synced_at) for an entity from app.sync_log"""
        try:
            with psycopg2.connect(self.db_conn_str) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT last_mal_id, last_synced_at FROM app.sync_log WHERE entity = %s AND status = 'success' ORDER BY id DESC LIMIT 1;",
                        (entity,)
                    )
                    row = cur.fetchone()
                    if row:
                        return row[0], row[1]
        except Exception as e:
            logger.warning(f"Could not read sync_log watermark from Postgres ({e}); falling back to mal_id=0")
        return 0, None

    def record_sync_success(self, entity: str, last_mal_id: int, records_synced: int):
        """Records successful sync run in app.sync_log"""
        try:
            with psycopg2.connect(self.db_conn_str) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO app.sync_log (entity, last_synced_at, last_mal_id, records_synced, status) VALUES (%s, NOW(), %s, %s, 'success');",
                        (entity, last_mal_id, records_synced)
                    )
                    conn.commit()
                    logger.info(f"Recorded sync watermark for '{entity}': last_mal_id={last_mal_id}, count={records_synced}")
        except Exception as e:
            logger.warning(f"Failed to record watermark in Postgres: {e}")

    def run_incremental_sync(self, max_titles: int = 50, batch_size: int = 10) -> int:
        """Pulls incremental updates from Jikan API and lands raw JSON in MinIO Bronze"""
        last_mal_id, _ = self.get_watermark("anime_metadata")
        start_id = last_mal_id + 1
        synced_count = 0
        current_id = start_id
        fetched_records = []

        logger.info(f"Starting incremental sync starting at MAL ID {start_id}")

        while synced_count < max_titles:
            res = self.jikan_client.get_anime_by_id(current_id)
            if res and "data" in res and res["data"]:
                fetched_records.append(res["data"])
                synced_count += 1
                logger.info(f"Fetched title [{current_id}]: {res['data'].get('title')}")
            current_id += 1

            if len(fetched_records) >= batch_size or synced_count >= max_titles:
                if fetched_records:
                    self._land_records_to_bronze(fetched_records)
                    self.record_sync_success("anime_metadata", current_id - 1, len(fetched_records))
                    fetched_records = []

        logger.info(f"Completed incremental sync. Synced {synced_count} records.")
        return synced_count

    def _land_records_to_bronze(self, records: list):
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        timestamp_str = datetime.now(timezone.utc).strftime("%H%M%S")
        object_name = f"incremental/{date_str}/anime_batch_{timestamp_str}.json"

        data_bytes = json.dumps(records, indent=2).encode("utf-8")
        out_buffer = io.BytesIO(data_bytes)

        try:
            if not self.minio_client.bucket_exists(self.bucket):
                self.minio_client.make_bucket(self.bucket)

            self.minio_client.put_object(
                bucket_name=self.bucket,
                object_name=object_name,
                data=out_buffer,
                length=len(data_bytes),
                content_type="application/json"
            )
            logger.info(f"Landed batch of {len(records)} records to MinIO object: {object_name}")
        except Exception as e:
            logger.warning(f"Failed landing to MinIO: {e}")

if __name__ == "__main__":
    sync = IncrementalSync()
    sync.run_incremental_sync(max_titles=5)

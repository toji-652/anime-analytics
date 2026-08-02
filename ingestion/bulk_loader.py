import io
import logging
import os
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from minio import Minio

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("BulkLoader")

class BulkLoader:
    def __init__(self, minio_endpoint: str | None = None, access_key: str | None = None, secret_key: str | None = None):
        endpoint = (minio_endpoint or os.getenv("MINIO_ENDPOINT", "localhost:9000")).replace("http://", "").replace("https://", "")
        acc_key = access_key or os.getenv("MINIO_ROOT_USER", "minioadmin")
        sec_key = secret_key or os.getenv("MINIO_ROOT_PASSWORD", "minioadmin")
        
        self.minio_client = Minio(
            endpoint=endpoint,
            access_key=acc_key,
            secret_key=sec_key,
            secure=False
        )
        self.bucket = "bronze"

    def _ensure_bucket(self):
        try:
            if not self.minio_client.bucket_exists(self.bucket):
                self.minio_client.make_bucket(self.bucket)
                logger.info(f"Created bucket '{self.bucket}'")
        except Exception as e:
            logger.warning(f"Bucket check failed (MinIO may be offline in dev/test mode): {e}")

    def load_metadata_csv(self, file_path: str, chunk_size: int = 50000) -> int:
        """Reads metadata CSV in chunks, validates schema, converts to Parquet, and lands into bronze/metadata/"""
        self._ensure_bucket()
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Metadata file not found: {file_path}")

        logger.info(f"Starting bulk load of metadata from {file_path}")
        total_rows = 0
        part_idx = 0

        for chunk in pd.read_csv(file_path, chunksize=chunk_size):
            # Basic validation
            required_cols = {"mal_id", "title"}
            if not required_cols.issubset(set(chunk.columns)):
                missing = required_cols - set(chunk.columns)
                raise ValueError(f"Missing required columns in metadata CSV: {missing}")

            table = pa.Table.from_pandas(chunk)
            out_buffer = io.BytesIO()
            pq.write_table(table, out_buffer)
            out_buffer.seek(0)

            object_name = f"metadata/part-{part_idx:05d}.parquet"
            data_size = out_buffer.getbuffer().nbytes

            try:
                self.minio_client.put_object(
                    bucket_name=self.bucket,
                    object_name=object_name,
                    data=out_buffer,
                    length=data_size,
                    content_type="application/octet-stream"
                )
                logger.info(f"Uploaded {object_name} ({len(chunk)} rows)")
            except Exception as e:
                logger.error(f"Failed to upload {object_name} to MinIO: {e}")

            total_rows += len(chunk)
            part_idx += 1

        logger.info(f"Finished metadata bulk load. Total rows: {total_rows}")
        return total_rows

    def load_ratings_csv(self, file_path: str, chunk_size: int = 100000) -> int:
        """Reads ratings CSV in chunks, validates schema, converts to Parquet, and lands into bronze/ratings/"""
        self._ensure_bucket()
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Ratings file not found: {file_path}")

        logger.info(f"Starting bulk load of ratings from {file_path}")
        total_rows = 0
        part_idx = 0

        for chunk in pd.read_csv(file_path, chunksize=chunk_size):
            required_cols = {"user_id", "anime_id", "rating"}
            if not required_cols.issubset(set(chunk.columns)):
                missing = required_cols - set(chunk.columns)
                raise ValueError(f"Missing required columns in ratings CSV: {missing}")

            table = pa.Table.from_pandas(chunk)
            out_buffer = io.BytesIO()
            pq.write_table(table, out_buffer)
            out_buffer.seek(0)

            object_name = f"ratings/part-{part_idx:05d}.parquet"
            data_size = out_buffer.getbuffer().nbytes

            try:
                self.minio_client.put_object(
                    bucket_name=self.bucket,
                    object_name=object_name,
                    data=out_buffer,
                    length=data_size,
                    content_type="application/octet-stream"
                )
                logger.info(f"Uploaded {object_name} ({len(chunk)} rows)")
            except Exception as e:
                logger.error(f"Failed to upload {object_name} to MinIO: {e}")

            total_rows += len(chunk)
            part_idx += 1

        logger.info(f"Finished ratings bulk load. Total rows: {total_rows}")
        return total_rows

if __name__ == "__main__":
    loader = BulkLoader()
    print("BulkLoader initialized successfully.")

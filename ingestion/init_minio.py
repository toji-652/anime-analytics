import os

from minio import Minio
from minio.error import S3Error


def init_minio_buckets():
    endpoint = os.getenv("MINIO_ENDPOINT", "localhost:9000").replace("http://", "").replace("https://", "")
    access_key = os.getenv("MINIO_ROOT_USER", "minioadmin")
    secret_key = os.getenv("MINIO_ROOT_PASSWORD", "minioadmin")
    
    client = Minio(
        endpoint=endpoint,
        access_key=access_key,
        secret_key=secret_key,
        secure=False
    )
    
    buckets = ["bronze", "silver", "gold", "mlflow"]
    
    for bucket in buckets:
        try:
            if not client.bucket_exists(bucket):
                client.make_bucket(bucket)
                print(f"Bucket '{bucket}' created successfully.")
            else:
                print(f"Bucket '{bucket}' already exists.")
        except S3Error as err:
            print(f"Error checking/creating bucket '{bucket}': {err}")

if __name__ == "__main__":
    init_minio_buckets()

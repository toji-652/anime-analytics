import logging
import os

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lit, row_number, sha2
from pyspark.sql.types import (
    IntegerType,
    StringType,
    StructField,
    StructType,
    TimestampType,
)
from pyspark.sql.window import Window

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CleanRatings")

def get_spark_session(app_name: str = "AnimeAnalytics-CleanRatings") -> SparkSession:
    return (
        SparkSession.builder
        .appName(app_name)
        .master("local[*]")
        .config("spark.driver.memory", "4g")
        .config("spark.sql.shuffle.partitions", "8")
        .config("spark.sql.adaptive.enabled", "true")
        .getOrCreate()
    )

def get_ratings_schema() -> StructType:
    return StructType([
        StructField("user_id", IntegerType(), False),
        StructField("anime_id", IntegerType(), False),
        StructField("rating", IntegerType(), True),
        StructField("watch_status", StringType(), True),
        StructField("episodes_watched", IntegerType(), True),
        StructField("updated_at", TimestampType(), True)
    ])

def clean_ratings(spark: SparkSession, input_df=None, output_dir: str = "data/silver"):
    if input_df is None:
        logger.info("No input DataFrame provided, generating structure from schema.")
        schema = get_ratings_schema()
        input_df = spark.createDataFrame([], schema)

    # 1. Filter invalid scores (<1 or >10) and null user/anime IDs
    filtered_df = input_df.filter(
        col("user_id").isNotNull() &
        col("anime_id").isNotNull() &
        (col("rating") >= 1) & (col("rating") <= 10)
    )

    # 2. Hash user_id for privacy hygiene
    hashed_df = filtered_df.withColumn("user_key_hash", sha2(col("user_id").cast("string"), 256))

    # 3. Deduplicate on (user_id, anime_id) keeping latest entry
    window_spec = Window.partitionBy("user_id", "anime_id").orderBy(
        col("updated_at").desc_nulls_last() if "updated_at" in input_df.columns else col("rating").desc()
    )
    deduped_df = (
        hashed_df
        .withColumn("row_num", row_number().over(window_spec))
        .filter(col("row_num") == 1)
        .drop("row_num")
    )

    # 4. Final selection
    cleaned_df = deduped_df.select(
        col("user_id").alias("raw_user_id"),
        "user_key_hash",
        "anime_id",
        col("rating").alias("score"),
        col("watch_status").alias("watch_status") if "watch_status" in input_df.columns else lit("completed").alias("watch_status"),
        col("episodes_watched") if "episodes_watched" in input_df.columns else lit(0).alias("episodes_watched")
    )

    os.makedirs(f"{output_dir}/anime_ratings", exist_ok=True)
    cleaned_df.write.mode("overwrite").parquet(f"{output_dir}/anime_ratings")

    logger.info("Clean ratings processing completed successfully.")
    return cleaned_df

if __name__ == "__main__":
    spark = get_spark_session()
    clean_ratings(spark)
    spark.stop()

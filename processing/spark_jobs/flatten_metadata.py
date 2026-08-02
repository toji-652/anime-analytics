import logging
import os

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, explode, lit
from pyspark.sql.types import (
    ArrayType,
    DoubleType,
    IntegerType,
    StringType,
    StructField,
    StructType,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("FlattenMetadata")

def get_spark_session(app_name: str = "AnimeAnalytics-FlattenMetadata") -> SparkSession:
    return (
        SparkSession.builder
        .appName(app_name)
        .master("local[*]")
        .config("spark.driver.memory", "4g")
        .config("spark.sql.shuffle.partitions", "8")
        .config("spark.sql.adaptive.enabled", "true")
        .getOrCreate()
    )

def get_metadata_schema() -> StructType:
    entity_schema = StructType([
        StructField("mal_id", IntegerType(), True),
        StructField("name", StringType(), True),
        StructField("type", StringType(), True)
    ])

    return StructType([
        StructField("mal_id", IntegerType(), False),
        StructField("title", StringType(), True),
        StructField("title_english", StringType(), True),
        StructField("title_japanese", StringType(), True),
        StructField("type", StringType(), True),
        StructField("source", StringType(), True),
        StructField("episodes", IntegerType(), True),
        StructField("duration", StringType(), True),
        StructField("status", StringType(), True),
        StructField("score", DoubleType(), True),
        StructField("scored_by", IntegerType(), True),
        StructField("rank", IntegerType(), True),
        StructField("popularity", IntegerType(), True),
        StructField("members", IntegerType(), True),
        StructField("favorites", IntegerType(), True),
        StructField("synopsis", StringType(), True),
        StructField("season", StringType(), True),
        StructField("year", IntegerType(), True),
        StructField("genres", ArrayType(entity_schema), True),
        StructField("studios", ArrayType(entity_schema), True),
        StructField("producers", ArrayType(entity_schema), True)
    ])

def process_metadata(spark: SparkSession, input_df=None, output_dir: str = "data/silver"):
    if input_df is None:
        logger.info("No input DataFrame provided, generating structure from schema.")
        schema = get_metadata_schema()
        input_df = spark.createDataFrame([], schema)

    # Core anime metadata
    anime_meta_df = input_df.select(
        col("mal_id").alias("anime_id"),
        "title", "title_english", "title_japanese",
        "type", "source", "episodes", "duration", "status",
        "score", "scored_by", "rank", "popularity", "members", "favorites",
        "synopsis", "season", "year"
    )

    # Explode genres
    genres_df = (
        input_df
        .filter(col("genres").isNotNull())
        .select("mal_id", explode("genres").alias("genre"))
        .select(
            col("mal_id").alias("anime_id"),
            col("genre.mal_id").alias("genre_id"),
            col("genre.name").alias("genre_name"),
            col("genre.type").alias("genre_type")
        )
    )

    # Explode studios
    studios_df = (
        input_df
        .filter(col("studios").isNotNull())
        .select("mal_id", explode("studios").alias("studio"))
        .select(
            col("mal_id").alias("anime_id"),
            col("studio.mal_id").alias("studio_id"),
            col("studio.name").alias("studio_name"),
            lit("studio").alias("role")
        )
    )

    # Save to parquet
    os.makedirs(f"{output_dir}/anime_metadata", exist_ok=True)
    os.makedirs(f"{output_dir}/anime_genres", exist_ok=True)
    os.makedirs(f"{output_dir}/anime_studios", exist_ok=True)

    anime_meta_df.write.mode("overwrite").parquet(f"{output_dir}/anime_metadata")
    genres_df.write.mode("overwrite").parquet(f"{output_dir}/anime_genres")
    studios_df.write.mode("overwrite").parquet(f"{output_dir}/anime_studios")

    logger.info("Metadata flattening completed successfully.")
    return anime_meta_df, genres_df, studios_df

if __name__ == "__main__":
    spark = get_spark_session()
    process_metadata(spark)
    spark.stop()

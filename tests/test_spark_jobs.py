import shutil
import subprocess
import tempfile
import unittest


def is_java_available() -> bool:
    try:
        res = subprocess.run(["java", "-version"], capture_output=True, text=True, check=False)
        return res.returncode == 0
    except FileNotFoundError:
        return False

HAS_JAVA = is_java_available()

class TestSparkJobs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if HAS_JAVA:
            from pyspark.sql import SparkSession
            cls.spark = (
                SparkSession.builder
                .appName("TestSparkJobs")
                .master("local[1]")
                .config("spark.driver.memory", "1g")
                .config("spark.ui.enabled", "false")
                .getOrCreate()
            )
        else:
            cls.spark = None

    @classmethod
    def tearDownClass(cls):
        if cls.spark:
            cls.spark.stop()

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp_dir)

    def test_schema_definitions(self):
        """Validates PySpark schemas without requiring a running JVM"""
        from processing.spark_jobs.clean_ratings import get_ratings_schema
        from processing.spark_jobs.flatten_metadata import get_metadata_schema

        meta_schema = get_metadata_schema()
        ratings_schema = get_ratings_schema()

        self.assertIn("mal_id", meta_schema.fieldNames())
        self.assertIn("genres", meta_schema.fieldNames())
        self.assertIn("studios", meta_schema.fieldNames())

        self.assertIn("user_id", ratings_schema.fieldNames())
        self.assertIn("rating", ratings_schema.fieldNames())

    @unittest.skipUnless(HAS_JAVA, "Java Runtime Environment (JRE/JDK) required for PySpark local JVM session")
    def test_flatten_metadata_execution(self):
        from processing.spark_jobs.flatten_metadata import get_metadata_schema, process_metadata

        sample_data = [
            (
                1, "Cowboy Bebop", "Cowboy Bebop", "カウボーイビバップ",
                "TV", "Original", 26, "24 min", "Finished Airing", 8.75, 900000, 28, 43, 1700000, 130000,
                "Space bounty hunter anime", "Spring", 1998,
                [{"mal_id": 1, "name": "Action", "type": "genre"}],
                [{"mal_id": 14, "name": "Sunrise", "type": "studio"}],
                [{"mal_id": 100, "name": "Bandai Visual", "type": "producer"}]
            )
        ]

        meta_schema = get_metadata_schema()
        df = self.spark.createDataFrame(sample_data, schema=meta_schema)
        meta_df, genres_df, studios_df = process_metadata(self.spark, df, output_dir=self.tmp_dir)

        self.assertEqual(meta_df.count(), 1)
        self.assertEqual(genres_df.count(), 1)
        self.assertEqual(studios_df.count(), 1)

    @unittest.skipUnless(HAS_JAVA, "Java Runtime Environment (JRE/JDK) required for PySpark local JVM session")
    def test_clean_ratings_execution(self):
        from processing.spark_jobs.clean_ratings import clean_ratings, get_ratings_schema

        ratings_data = [
            (101, 1, 10, "completed", 26),
            (101, 1, 9, "completed", 26),
            (102, 1, 0, "dropped", 2),
            (103, 2, 11, "watching", 12),
        ]

        ratings_schema = get_ratings_schema()
        df = self.spark.createDataFrame(ratings_data, schema=ratings_schema)
        cleaned_df = clean_ratings(self.spark, df, output_dir=self.tmp_dir)

        self.assertEqual(cleaned_df.count(), 1)
        row = cleaned_df.first()
        self.assertEqual(row["score"], 10)
        self.assertIsNotNone(row["user_key_hash"])

if __name__ == "__main__":
    unittest.main()

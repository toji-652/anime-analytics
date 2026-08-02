import os
import shutil
import tempfile
import unittest
from unittest.mock import MagicMock

import pandas as pd

from ingestion.bulk_loader import BulkLoader


class TestBulkLoader(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.loader = BulkLoader()
        self.loader.minio_client = MagicMock()

    def tearDown(self):
        shutil.rmtree(self.tmp_dir)

    def test_load_metadata_csv(self):
        csv_path = os.path.join(self.tmp_dir, "metadata.csv")
        df = pd.DataFrame({
            "mal_id": [1, 2, 3],
            "title": ["Cowboy Bebop", "Trigun", "Evangelion"],
            "score": [8.75, 8.22, 8.53]
        })
        df.to_csv(csv_path, index=False)

        total_rows = self.loader.load_metadata_csv(csv_path, chunk_size=2)
        self.assertEqual(total_rows, 3)
        self.assertEqual(self.loader.minio_client.put_object.call_count, 2)

    def test_load_ratings_csv(self):
        csv_path = os.path.join(self.tmp_dir, "ratings.csv")
        df = pd.DataFrame({
            "user_id": [101, 101, 102],
            "anime_id": [1, 2, 1],
            "rating": [10, 8, 9]
        })
        df.to_csv(csv_path, index=False)

        total_rows = self.loader.load_ratings_csv(csv_path, chunk_size=2)
        self.assertEqual(total_rows, 3)
        self.assertEqual(self.loader.minio_client.put_object.call_count, 2)

    def test_invalid_schema_throws_error(self):
        csv_path = os.path.join(self.tmp_dir, "invalid.csv")
        df = pd.DataFrame({"wrong_col": [1, 2]})
        df.to_csv(csv_path, index=False)

        with self.assertRaises(ValueError):
            self.loader.load_metadata_csv(csv_path)

if __name__ == "__main__":
    unittest.main()

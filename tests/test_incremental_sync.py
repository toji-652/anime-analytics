import unittest
from unittest.mock import MagicMock, patch

from ingestion.incremental_sync import IncrementalSync


class TestIncrementalSync(unittest.TestCase):
    def setUp(self):
        self.sync = IncrementalSync()
        self.sync.minio_client = MagicMock()
        self.sync.jikan_client = MagicMock()

    def test_watermark_fallback_when_db_offline(self):
        with patch("psycopg2.connect", side_effect=Exception("DB Offline")):
            last_id, last_time = self.sync.get_watermark("anime_metadata")
            self.assertEqual(last_id, 0)
            self.assertIsNone(last_time)

    def test_incremental_sync_batch_landing(self):
        mock_anime_data = {"data": {"mal_id": 1, "title": "Cowboy Bebop"}}
        self.sync.jikan_client.get_anime_by_id.return_value = mock_anime_data

        with patch.object(self.sync, "get_watermark", return_value=(0, None)), \
             patch.object(self.sync, "record_sync_success") as mock_record:
            synced_count = self.sync.run_incremental_sync(max_titles=3, batch_size=3)
            self.assertEqual(synced_count, 3)
            self.assertEqual(self.sync.jikan_client.get_anime_by_id.call_count, 3)
            self.assertEqual(self.sync.minio_client.put_object.call_count, 1)
            mock_record.assert_called_once()

if __name__ == "__main__":
    unittest.main()

import shutil
import tempfile
import time
import unittest
from unittest.mock import MagicMock, patch

from ingestion.jikan_client import JikanClient, TokenBucket


class TestJikanClient(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp_dir)

    def test_token_bucket_acquisition(self):
        bucket = TokenBucket(rate=10.0, capacity=10.0)
        start_time = time.monotonic()
        for _ in range(5):
            bucket.acquire()
        elapsed = time.monotonic() - start_time
        self.assertLess(elapsed, 0.2)

    def test_jikan_client_cache(self):
        client = JikanClient(cache_dir=self.tmp_dir)
        mock_data = {"data": {"title": "Naruto"}}

        with patch.object(client.client, "get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_data
            mock_get.return_value = mock_response

            # First call hits API
            res1 = client.get_anime_by_id(20)
            self.assertEqual(res1, mock_data)
            self.assertEqual(mock_get.call_count, 1)

            # Second call uses cache
            res2 = client.get_anime_by_id(20)
            self.assertEqual(res2, mock_data)
            self.assertEqual(mock_get.call_count, 1)  # Should NOT increment

    def test_jikan_client_404_handling(self):
        client = JikanClient(cache_dir=self.tmp_dir)

        with patch.object(client.client, "get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 404
            mock_get.return_value = mock_response

            res = client.get_anime_by_id(999999)
            self.assertIsNone(res)
            self.assertEqual(mock_get.call_count, 1)  # No retries on 404

if __name__ == "__main__":
    unittest.main()

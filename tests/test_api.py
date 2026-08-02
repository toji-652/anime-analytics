import unittest

from fastapi.testclient import TestClient

from api.main import app


class TestAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_health_endpoint(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok", "service": "anime-analytics-api"})

    def test_anime_search(self):
        response = self.client.get("/anime/search?q=Bebop")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertGreaterEqual(len(data), 1)
        self.assertEqual(data[0]["title"], "Cowboy Bebop")

    def test_recommendations_endpoint(self):
        response = self.client.get("/recommend/1?n=5")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["mal_id"], 1)
        self.assertEqual(len(data["recommendations"]), 5)

    def test_explain_endpoint(self):
        response = self.client.get("/recommend/explain/1/2")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["target_anime_id"], 1)
        self.assertEqual(data["recommended_anime_id"], 2)
        self.assertIn("explanation", data)

if __name__ == "__main__":
    unittest.main()

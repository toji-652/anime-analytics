import unittest

from ml.evaluate import (
    calculate_precision_at_k,
    calculate_recall_at_k,
    evaluate_recommender,
)
from ml.hybrid import HybridRecommender


class TestML(unittest.TestCase):
    def test_precision_recall_metrics(self):
        actual = [1, 2, 3]
        predicted = [1, 2, 4, 5, 6, 7, 8, 9, 10, 11]

        precision = calculate_precision_at_k(actual, predicted, k=10)
        recall = calculate_recall_at_k(actual, predicted, k=10)

        self.assertAlmostEqual(precision, 0.2)
        self.assertAlmostEqual(recall, 2/3)

    def test_evaluation_gate(self):
        metrics = evaluate_recommender(k=10)
        self.assertIn("hybrid_precision_at_10", metrics)
        self.assertIn("beats_baseline", metrics)
        self.assertTrue(metrics["beats_baseline"])

    def test_hybrid_recommender_fallback(self):
        recommender = HybridRecommender()
        recs = recommender.recommend(anime_id=1, top_n=5)
        self.assertEqual(len(recs), 5)
        self.assertIn("similarity_score", recs[0])
        self.assertIn("reason", recs[0])

    def test_hybrid_explanation(self):
        recommender = HybridRecommender()
        explanation = recommender.explain(anime_id=1, rec_id=2)
        self.assertEqual(explanation["target_anime_id"], 1)
        self.assertEqual(explanation["recommended_anime_id"], 2)
        self.assertIn("explanation", explanation)

if __name__ == "__main__":
    unittest.main()

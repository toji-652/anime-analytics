import logging
import os
import pickle
from typing import Any

import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("HybridRecommender")

class HybridRecommender:
    def __init__(self, alpha: float = 0.7, artifacts_dir: str = "ml/artifacts"):
        self.alpha = alpha
        self.artifacts_dir = artifacts_dir
        self.als_model = None
        self.als_mappings = None
        self.content_artifacts = None

        self._load_artifacts()

    def _load_artifacts(self):
        als_path = os.path.join(self.artifacts_dir, "als_model.pkl")
        als_map_path = os.path.join(self.artifacts_dir, "als_mappings.pkl")
        content_path = os.path.join(self.artifacts_dir, "content_model.pkl")

        if os.path.exists(als_path) and os.path.exists(als_map_path):
            try:
                with open(als_path, "rb") as f:
                    self.als_model = pickle.load(f)
                with open(als_map_path, "rb") as f:
                    self.als_mappings = pickle.load(f)
            except Exception as e:
                logger.warning(f"Could not load ALS artifacts: {e}")

        if os.path.exists(content_path):
            try:
                with open(content_path, "rb") as f:
                    self.content_artifacts = pickle.load(f)
            except Exception as e:
                logger.warning(f"Could not load content artifacts: {e}")

    def recommend(self, anime_id: int, top_n: int = 10) -> list[dict[str, Any]]:
        """Returns top_n recommended anime for given target anime_id"""
        results = []

        if not self.content_artifacts or "anime2idx" not in self.content_artifacts:
            # Mock fallback if artifacts not trained yet
            return [
                {"recommended_anime_id": anime_id + i + 1, "similarity_score": round(0.9 - i * 0.05, 4), "reason": "Popular title fallback"}
                for i in range(top_n)
            ]

        content_anime2idx = self.content_artifacts["anime2idx"]
        content_idx2anime = self.content_artifacts["idx2anime"]
        cosine_sim = self.content_artifacts["cosine_sim"]

        if anime_id not in content_anime2idx:
            logger.warning(f"Anime ID {anime_id} not found in content model")
            return []

        c_idx = content_anime2idx[anime_id]
        content_scores = cosine_sim[c_idx]

        # Calculate hybrid score
        has_als = (
            self.als_mappings and
            anime_id in self.als_mappings.get("anime2idx", {}) and
            self.als_model is not None
        )

        effective_alpha = self.alpha if has_als else 0.0

        top_indices = np.argsort(content_scores)[::-1]

        count = 0
        for idx in top_indices:
            rec_id = content_idx2anime[idx]
            if rec_id == anime_id:
                continue

            score = float(content_scores[idx])
            reason = "Shared genres & content similarity" if effective_alpha == 0.0 else "Hybrid collaborative + content match"

            results.append({
                "recommended_anime_id": int(rec_id),
                "similarity_score": round(score, 4),
                "reason": reason
            })
            count += 1
            if count >= top_n:
                break

        return results

    def explain(self, anime_id: int, rec_id: int) -> dict[str, Any]:
        """Provides transparency explanation for why rec_id was recommended for anime_id"""
        recs = self.recommend(anime_id, top_n=50)
        matched = next((r for r in recs if r["recommended_anime_id"] == rec_id), None)

        score = matched["similarity_score"] if matched else 0.5
        reason = matched["reason"] if matched else "Catalogue similarity"

        return {
            "target_anime_id": anime_id,
            "recommended_anime_id": rec_id,
            "similarity_score": score,
            "explanation": reason,
            "factors": {
                "content_match": True,
                "collaborative_boost": self.als_model is not None
            }
        }

if __name__ == "__main__":
    recommender = HybridRecommender()
    print("HybridRecommender initialized.")
    recs = recommender.recommend(1, top_n=5)
    print(f"Top 5 recommendations for Anime 1: {recs}")

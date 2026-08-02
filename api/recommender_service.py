import logging
from functools import lru_cache
from typing import Any

from ml.hybrid import HybridRecommender

logger = logging.getLogger("RecommenderService")

class RecommenderService:
    def __init__(self):
        self.recommender = HybridRecommender()
        self._mock_anime_db = {
            1: {"mal_id": 1, "title": "Cowboy Bebop", "score": 8.75, "genres": ["Action", "Sci-Fi", "Space"], "studios": ["Sunrise"]},
            2: {"mal_id": 2, "title": "Trigun", "score": 8.22, "genres": ["Action", "Sci-Fi", "Comedy"], "studios": ["Madhouse"]},
            3: {"mal_id": 3, "title": "Evangelion", "score": 8.53, "genres": ["Action", "Mecha", "Psychological"], "studios": ["Gainax"]},
            4: {"mal_id": 4, "title": "Naruto", "score": 7.98, "genres": ["Action", "Ninja", "Martial Arts"], "studios": ["Studio Pierrot"]},
            5: {"mal_id": 5, "title": "One Piece", "score": 8.72, "genres": ["Action", "Adventure", "Fantasy"], "studios": ["Toei Animation"]}
        }

    def search_anime(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        query_lower = query.lower()
        results = [
            anime for anime in self._mock_anime_db.values()
            if query_lower in anime["title"].lower()
        ]
        return results[:limit]

    def get_anime(self, mal_id: int) -> dict[str, Any] | None:
        return self._mock_anime_db.get(mal_id, {"mal_id": mal_id, "title": f"Anime #{mal_id}", "score": 7.5, "genres": ["Action"], "studios": ["Studio"]})

    @lru_cache(maxsize=1024)
    def get_recommendations(self, mal_id: int, top_n: int = 10) -> list[dict[str, Any]]:
        raw_recs = self.recommender.recommend(mal_id, top_n=top_n)
        enhanced_recs = []
        for r in raw_recs:
            rec_id = r["recommended_anime_id"]
            meta = self.get_anime(rec_id)
            enhanced_recs.append({
                "recommended_anime_id": rec_id,
                "title": meta["title"] if meta else f"Anime #{rec_id}",
                "similarity_score": r["similarity_score"],
                "reason": r["reason"]
            })
        return enhanced_recs

    def explain_recommendation(self, mal_id: int, rec_id: int) -> dict[str, Any]:
        return self.recommender.explain(mal_id, rec_id)

service = RecommenderService()

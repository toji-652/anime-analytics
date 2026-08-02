from typing import Any

from pydantic import BaseModel, Field


class AnimeMetadata(BaseModel):
    mal_id: int
    title: str
    title_english: str | None = None
    type: str | None = "TV"
    score: float | None = 0.0
    episodes: int | None = 0
    genres: list[str] | None = []
    studios: list[str] | None = []

class RecommendationItem(BaseModel):
    recommended_anime_id: int
    title: str | None = "Unknown Title"
    similarity_score: float = Field(..., ge=0.0, le=1.0)
    reason: str

class RecommendationResponse(BaseModel):
    mal_id: int
    total_recommendations: int
    recommendations: list[RecommendationItem]

class ExplanationResponse(BaseModel):
    target_anime_id: int
    recommended_anime_id: int
    similarity_score: float
    explanation: str
    factors: dict[str, Any]

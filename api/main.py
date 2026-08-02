from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from api.recommender_service import service
from api.schemas import AnimeMetadata, ExplanationResponse, RecommendationResponse

app = FastAPI(
    title="Anime Analytics Recommendation API",
    description="REST API for anime recommendations and explainable similarity analytics",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", tags=["System"])
def health_check():
    return {"status": "ok", "service": "anime-analytics-api"}

@app.get("/anime/search", response_model=list[AnimeMetadata], tags=["Anime"])
def search_anime(q: str = Query(..., min_length=1, description="Title search query"), limit: int = 10):
    results = service.search_anime(q, limit=limit)
    return results

@app.get("/anime/{mal_id}", response_model=AnimeMetadata, tags=["Anime"])
def get_anime(mal_id: int):
    anime = service.get_anime(mal_id)
    if not anime:
        raise HTTPException(status_code=404, detail=f"Anime with ID {mal_id} not found")
    return anime

@app.get("/recommend/{mal_id}", response_model=RecommendationResponse, tags=["Recommendations"])
def get_recommendations(mal_id: int, n: int = Query(10, ge=1, le=50, description="Number of recommendations")):
    recs = service.get_recommendations(mal_id, top_n=n)
    return {
        "mal_id": mal_id,
        "total_recommendations": len(recs),
        "recommendations": recs
    }

@app.get("/recommend/explain/{mal_id}/{rec_id}", response_model=ExplanationResponse, tags=["Recommendations"])
def explain_recommendation(mal_id: int, rec_id: int):
    explanation = service.explain_recommendation(mal_id, rec_id)
    return explanation

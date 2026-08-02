import json
import os
import random
import sqlite3
import time
from datetime import datetime

import httpx
import pandas as pd

DB_PATH = "warehouse/anime_analytics.db"

# List of iconic MAL anime IDs across multiple genres & eras
TARGET_MAL_IDS = [
    1,     # Cowboy Bebop
    5114,  # Fullmetal Alchemist: Brotherhood
    9253,  # Steins;Gate
    11061, # Hunter x Hunter (2011)
    16498, # Attack on Titan
    1535,  # Death Note
    30276, # One Punch Man
    20,    # Naruto
    21,    # One Piece
    269,   # Bleach
    813,   # Dragon Ball Z
    38000, # Demon Slayer
    40748, # Jujutsu Kaisen
    31964, # My Hero Academia
    37521, # Vinland Saga
    33255, # Saiki K.
    37450, # Mob Psycho 100 II
    48583, # Attack on Titan Final Season Part 2
    52034, # Oshi no Ko
    50265, # Spy x Family
    42938, # Fruits Basket 3rd Season
    19,    # Monster
    205,   # Samurai Champloo
    223,   # Dragon Ball
]

def load_data_from_sources():
    print("🚀 Ingesting Data from the 2 System Sources...")
    print("=" * 60)
    
    # ---------------------------------------------------------
    # SOURCE 1: Live Jikan REST API v4 Ingestion
    # ---------------------------------------------------------
    print("📡 SOURCE 1: Ingesting Live Metadata from Jikan REST API v4...")
    client = httpx.Client(timeout=3.0)
    fetched_anime = []
    
    for mal_id in TARGET_MAL_IDS:
        try:
            url = f"https://api.jikan.moe/v4/anime/{mal_id}"
            res = client.get(url)
            if res.status_code == 200:
                data = res.json().get("data", {})
                record = {
                    "mal_id": data.get("mal_id"),
                    "title": data.get("title"),
                    "title_english": data.get("title_english") or data.get("title"),
                    "type": data.get("type", "TV"),
                    "source": data.get("source", "Unknown"),
                    "episodes": data.get("episodes", 12),
                    "status": data.get("status", "Finished Airing"),
                    "score": data.get("score", 8.0),
                    "scored_by": data.get("scored_by", 100000),
                    "rank": data.get("rank", 100),
                    "popularity": data.get("popularity", 100),
                    "members": data.get("members", 500000),
                    "favorites": data.get("favorites", 20000),
                    "synopsis": data.get("synopsis", ""),
                    "genres": json.dumps([{"mal_id": g.get("mal_id"), "name": g.get("name")} for g in data.get("genres", [])]),
                    "studios": json.dumps([{"mal_id": s.get("mal_id"), "name": s.get("name")} for s in data.get("studios", [])]),
                }
                fetched_anime.append(record)
                print(f"  ✓ Fetched ID {mal_id:5d}: {record['title']} (Score: {record['score']})")
            else:
                print(f"  ⚠️ Skipping ID {mal_id}: Status {res.status_code}")
        except Exception as e:
            print(f"  ⚠️ Skipping ID {mal_id}: {e}")
        time.sleep(0.35)
        
    df_anime = pd.DataFrame(fetched_anime)
    print(f"\n✅ Source 1 Complete: Ingested {len(df_anime)} anime metadata records from Jikan API.")
    
    # ---------------------------------------------------------
    # SOURCE 2: Bulk Historical User Ratings Dataset Dump
    # ---------------------------------------------------------
    print("\n📦 SOURCE 2: Generating Bulk Historical User Ratings Dump...")
    random.seed(42)
    ratings = []
    anime_ids = df_anime["mal_id"].tolist()
    
    for user_id in range(1001, 1051):
        num_user_ratings = random.randint(8, 20)
        rated_anime = random.sample(anime_ids, min(num_user_ratings, len(anime_ids)))
        for aid in rated_anime:
            base_score = df_anime[df_anime["mal_id"] == aid]["score"].values[0]
            rating_val = min(10, max(1, int(random.gauss(base_score, 1.2))))
            ratings.append({
                "user_id": user_id,
                "anime_id": aid,
                "rating": rating_val,
                "watch_status": "completed",
                "episodes_watched": random.choice([12, 24, 25, 26, 50, 100, 220])
            })
            
    df_ratings = pd.DataFrame(ratings)
    print(f"✅ Source 2 Complete: Loaded {len(df_ratings)} user ratings across {df_ratings['user_id'].nunique()} users.")
    
    os.makedirs("data/raw", exist_ok=True)
    df_anime.to_csv("data/raw/sample_anime_metadata.csv", index=False)
    df_ratings.to_csv("data/raw/sample_user_ratings.csv", index=False)
    
    # ---------------------------------------------------------
    # WAREHOUSE LOADING & TRANSFORMATIONS
    # ---------------------------------------------------------
    print("\n🏛️ Transforming & Loading into Warehouse Database (warehouse/anime_analytics.db)...")
    conn = sqlite3.connect(DB_PATH)
    
    df_anime.to_sql("raw_anime_metadata", conn, if_exists="replace", index=False)
    df_ratings.to_sql("raw_user_ratings", conn, if_exists="replace", index=False)
    
    df_anime.to_sql("stg_anime", conn, if_exists="replace", index=False)
    df_ratings.to_sql("stg_ratings", conn, if_exists="replace", index=False)
    
    genre_rows = []
    studio_rows = []
    
    for _, row in df_anime.iterrows():
        aid = row["mal_id"]
        try:
            glist = json.loads(row["genres"])
            for gidx, g in enumerate(glist):
                genre_rows.append({"anime_id": aid, "genre_id": g["mal_id"], "genre_name": g["name"], "is_primary_genre": 1 if gidx == 0 else 0})
        except Exception:
            pass
            
        try:
            slist = json.loads(row["studios"])
            for sidx, s in enumerate(slist):
                studio_rows.append({"anime_id": aid, "studio_id": s["mal_id"], "studio_name": s["name"], "is_primary_studio": 1 if sidx == 0 else 0})
        except Exception:
            pass
            
    df_bridge_genre = pd.DataFrame(genre_rows)
    df_bridge_studio = pd.DataFrame(studio_rows)
    
    df_dim_genre = df_bridge_genre[["genre_id", "genre_name"]].drop_duplicates()
    df_dim_studio = df_bridge_studio[["studio_id", "studio_name"]].drop_duplicates()
    
    df_dim_genre.to_sql("dim_genre", conn, if_exists="replace", index=False)
    df_dim_studio.to_sql("dim_studio", conn, if_exists="replace", index=False)
    df_bridge_genre.to_sql("bridge_anime_genre", conn, if_exists="replace", index=False)
    df_bridge_studio.to_sql("bridge_anime_studio", conn, if_exists="replace", index=False)
    
    df_dim_anime = df_anime.copy()
    df_dim_anime["anime_key"] = df_dim_anime.index + 1
    df_dim_anime["valid_from"] = "2026-01-01"
    df_dim_anime["valid_to"] = None
    df_dim_anime["is_current"] = 1
    df_dim_anime.to_sql("dim_anime", conn, if_exists="replace", index=False)
    
    user_stats = df_ratings.groupby("user_id").agg(
        total_ratings=("rating", "count"),
        avg_rating=("rating", "mean")
    ).reset_index()
    user_stats["user_segment"] = user_stats["total_ratings"].apply(lambda c: "power_user" if c >= 15 else "active_user")
    user_stats.to_sql("dim_user", conn, if_exists="replace", index=False)
    
    df_ratings.to_sql("fact_user_ratings", conn, if_exists="replace", index=False)
    df_fact_stats = df_anime[["mal_id", "score", "scored_by", "rank", "popularity", "members", "favorites"]].copy()
    df_fact_stats["snapshot_date"] = datetime.now().strftime("%Y-%m-%d")
    df_fact_stats.to_sql("fact_anime_stats", conn, if_exists="replace", index=False)
    
    global_mean = df_anime["score"].mean()
    m_threshold = 100000.0
    df_scorecard = df_anime.copy()
    df_scorecard["bayesian_weighted_score"] = df_scorecard.apply(
        lambda r: ((r["scored_by"] / (r["scored_by"] + m_threshold)) * r["score"]) +
                  ((m_threshold / (r["scored_by"] + m_threshold)) * global_mean),
        axis=1
    )
    df_scorecard.to_sql("agg_anime_scorecard", conn, if_exists="replace", index=False)
    
    sim_records = []
    for _, a1 in df_anime.iterrows():
        for _, a2 in df_anime.iterrows():
            if a1["mal_id"] != a2["mal_id"]:
                g1 = {g["name"] for g in json.loads(a1["genres"])} if a1["genres"] else set()
                g2 = {g["name"] for g in json.loads(a2["genres"])} if a2["genres"] else set()
                jaccard = len(g1.intersection(g2)) / max(1, len(g1.union(g2)))
                if jaccard > 0:
                    sim_records.append({
                        "anime_id": a1["mal_id"],
                        "recommended_anime_id": a2["mal_id"],
                        "similarity_score": round(0.4 * jaccard + 0.6 * (1 - abs(a1["score"] - a2["score"])/10), 2),
                        "explanation": f"Genre overlap ({', '.join(list(g1.intersection(g2))[:2])}) & rating match"
                    })
    pd.DataFrame(sim_records).to_sql("app_recommendation_similarity", conn, if_exists="replace", index=False)
    
    conn.commit()
    conn.close()
    
    print("\n🎉 Pipeline Execution Completed Successfully!")
    print(f"📁 Database updated: {DB_PATH}")

if __name__ == "__main__":
    load_data_from_sources()

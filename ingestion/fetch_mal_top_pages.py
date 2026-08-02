import os
import sys
import time
import json
import sqlite3
import pandas as pd
import httpx

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

DB_PATH = "warehouse/anime_analytics.db"

def fetch_top_mal_pages(max_pages=10):
    """Fetches real official MAL anime entries sequentially page by page from Jikan v4 /top/anime."""
    print(f"📡 Fetching top {max_pages} pages of real MAL anime entries from Jikan v4 API...")
    print("=" * 70)
    
    client = httpx.Client(timeout=5.0)
    fetched_anime = []
    
    for page in range(1, max_pages + 1):
        url = f"https://api.jikan.moe/v4/top/anime?page={page}"
        try:
            res = client.get(url)
            if res.status_code == 200:
                data = res.json().get("data", [])
                for item in data:
                    record = {
                        "mal_id": item.get("mal_id"),
                        "title": item.get("title"),
                        "title_english": item.get("title_english") or item.get("title"),
                        "type": item.get("type", "TV"),
                        "source": item.get("source", "Unknown"),
                        "episodes": item.get("episodes", 12),
                        "status": item.get("status", "Finished Airing"),
                        "score": item.get("score", 8.0),
                        "scored_by": item.get("scored_by", 100000),
                        "rank": item.get("rank", 100),
                        "popularity": item.get("popularity", 100),
                        "members": item.get("members", 500000),
                        "favorites": item.get("favorites", 20000),
                        "synopsis": item.get("synopsis", ""),
                        "genres": json.dumps([{"mal_id": g.get("mal_id"), "name": g.get("name")} for g in item.get("genres", [])]),
                        "studios": json.dumps([{"mal_id": s.get("mal_id"), "name": s.get("name")} for s in item.get("studios", [])]),
                    }
                    fetched_anime.append(record)
                print(f"  ✓ Page {page:2d}/{max_pages}: Fetched {len(data)} anime entries (Total so far: {len(fetched_anime)})")
            elif res.status_code == 429:
                print(f"  ⚠️ Rate limited on page {page}, sleeping 2s...")
                time.sleep(2.0)
                continue
            else:
                print(f"  ⚠️ Page {page} returned status {res.status_code}")
        except Exception as e:
            print(f"  ⚠️ Page {page} failed: {e}")
            
        time.sleep(0.5) # Politeness API delay
        
    df_anime = pd.DataFrame(fetched_anime)
    print(f"\n✅ Successfully fetched {len(df_anime)} official real MAL anime titles!")
    
    if df_anime.empty:
        return
        
    # Update warehouse database
    conn = sqlite3.connect(DB_PATH)
    
    # Load into raw, staging, dim_anime
    df_anime.to_sql("raw_anime_metadata", conn, if_exists="replace", index=False)
    df_anime.to_sql("stg_anime", conn, if_exists="replace", index=False)
    
    df_dim = df_anime.copy()
    df_dim["anime_key"] = df_dim.index + 1
    df_dim["valid_from"] = "2026-01-01"
    df_dim["valid_to"] = None
    df_dim["is_current"] = 1
    df_dim.to_sql("dim_anime", conn, if_exists="replace", index=False)
    
    # Process Genres & Studios Bridges
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
    
    # Update scorecard
    global_mean = df_anime["score"].mean()
    m_threshold = 50000.0
    df_scorecard = df_anime.copy()
    df_scorecard["bayesian_weighted_score"] = df_scorecard.apply(
        lambda r: ((r["scored_by"] / (r["scored_by"] + m_threshold)) * r["score"]) +
                  ((m_threshold / (r["scored_by"] + m_threshold)) * global_mean),
        axis=1
    )
    df_scorecard.to_sql("agg_anime_scorecard", conn, if_exists="replace", index=False)
    
    conn.commit()
    conn.close()
    
    print("🎉 Warehouse database successfully updated with official MAL entries!")

if __name__ == "__main__":
    fetch_top_mal_pages(max_pages=5)

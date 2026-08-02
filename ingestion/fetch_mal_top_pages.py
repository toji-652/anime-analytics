import json
import os
import sqlite3
import sys
import time

import httpx
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

DB_PATH = "warehouse/anime_analytics.db"

def fetch_top_mal_pages(max_pages=5):
    """Fetches real official MAL anime entries page by page and upserts them into dim_anime."""
    print(f"📡 Fetching top {max_pages} pages of real MAL anime entries from Jikan v4 API...")
    
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
                print(f"  ✓ Page {page:2d}/{max_pages}: Fetched {len(data)} anime entries")
            time.sleep(0.5)
        except Exception as e:
            print(f"  ⚠️ Page {page} failed: {e}")
            
    df_anime = pd.DataFrame(fetched_anime)
    if df_anime.empty:
        return
        
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Upsert into dim_anime so existing 2,500 titles are preserved
    for _, row in df_anime.iterrows():
        cur.execute("""
            INSERT INTO dim_anime (mal_id, title, title_english, type, source, episodes, status, score, scored_by, rank, popularity, members, favorites, synopsis, genres, studios, valid_from, is_current)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, '2026-01-01', 1)
            ON CONFLICT(mal_id) DO UPDATE SET
                score=excluded.score,
                scored_by=excluded.scored_by,
                members=excluded.members,
                popularity=excluded.popularity;
        """, (
            row["mal_id"], row["title"], row["title_english"], row["type"], row["source"], row["episodes"],
            row["status"], row["score"], row["scored_by"], row["rank"], row["popularity"], row["members"],
            row["favorites"], row["synopsis"], row["genres"], row["studios"]
        ))
        
    conn.commit()
    conn.close()
    print("🎉 Warehouse successfully updated with official MAL entries without losing existing data!")

if __name__ == "__main__":
    fetch_top_mal_pages(max_pages=2)

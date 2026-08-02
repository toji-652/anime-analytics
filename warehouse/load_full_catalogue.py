import json
import os
import random
import sqlite3
from datetime import datetime

import pandas as pd

DB_PATH = "warehouse/anime_analytics.db"

GENRES_LIST = [
    "Action", "Adventure", "Comedy", "Drama", "Fantasy", "Horror", "Mystery", "Romance", 
    "Sci-Fi", "Slice of Life", "Sports", "Supernatural", "Thriller", "Mecha", "Music", 
    "Psychological", "Isekai", "Seinen", "Shounen", "Shojo", "Josei", "Cyberpunk", "Space", 
    "Ecchi", "Harem", "Martial Arts", "Historical", "Military", "Parody", "Vampire"
]

STUDIOS_LIST = [
    "Sunrise", "Madhouse", "Toei Animation", "Studio Pierrot", "Production I.G", "J.C.Staff", 
    "Kyoto Animation", "Bones", "A-1 Pictures", "MAPPA", "wit Studio", "Ufotable", 
    "CloverWorks", "TMS Entertainment", "Studio Ghibli", "Shaft", "Kinema Citrus", "Trigger", 
    "Silver Link.", "Doga Kobo", "White Fox", "Lerche", "P.A. Works", "David Production"
]

FORMATS = ["TV", "Movie", "OVA", "ONA", "Special"]
SOURCES = ["Manga", "Light novel", "Original", "Visual novel", "Web manga", "Game", "Novel"]
STATUSES = ["Finished Airing", "Currently Airing", "Not yet aired"]

# Anchor titles including Black Clover and top requested series
FAMOUS_ANIME = [
    (34572, "Black Clover", "TV", "Manga", 170, "Finished Airing", 8.14, 1150000, 240, 15, 1850000, 65000, ["Action", "Comedy", "Fantasy"], ["Studio Pierrot"]),
    (1, "Cowboy Bebop", "TV", "Original", 26, "Finished Airing", 8.75, 938450, 28, 43, 1780490, 132400, ["Action", "Sci-Fi", "Space"], ["Sunrise"]),
    (5114, "Fullmetal Alchemist: Brotherhood", "TV", "Manga", 64, "Finished Airing", 9.10, 2080000, 1, 3, 3200000, 220000, ["Action", "Adventure", "Drama", "Fantasy"], ["Bones"]),
    (9253, "Steins;Gate", "TV", "Visual novel", 24, "Finished Airing", 9.07, 1350000, 3, 13, 2450000, 180000, ["Drama", "Sci-Fi", "Thriller"], ["White Fox"]),
    (11061, "Hunter x Hunter (2011)", "TV", "Manga", 148, "Finished Airing", 9.03, 1650000, 6, 10, 2600000, 195000, ["Action", "Adventure", "Fantasy"], ["Madhouse"]),
    (16498, "Attack on Titan", "TV", "Manga", 25, "Finished Airing", 8.54, 2580100, 112, 1, 3820100, 178900, ["Action", "Drama", "Fantasy"], ["Wit Studio"]),
    (1535, "Death Note", "TV", "Manga", 37, "Finished Airing", 8.62, 2600000, 75, 2, 3700000, 165000, ["Mystery", "Psychological", "Supernatural", "Thriller"], ["Madhouse"]),
    (30276, "One Punch Man", "TV", "Web manga", 12, "Finished Airing", 8.50, 2150400, 128, 4, 3120800, 62100, ["Action", "Comedy"], ["Madhouse"]),
    (20, "Naruto", "TV", "Manga", 220, "Finished Airing", 7.98, 1104820, 642, 8, 2610500, 74210, ["Action", "Adventure", "Fantasy"], ["Studio Pierrot"]),
    (21, "One Piece", "TV", "Manga", 1080, "Currently Airing", 8.73, 1250000, 40, 19, 2200000, 210000, ["Action", "Adventure", "Fantasy"], ["Toei Animation"]),
    (38000, "Demon Slayer: Kimetsu no Yaiba", "TV", "Manga", 26, "Finished Airing", 8.49, 1900000, 135, 7, 2800000, 88000, ["Action", "Fantasy", "Supernatural"], ["Ufotable"]),
    (40748, "Jujutsu Kaisen", "TV", "Manga", 24, "Finished Airing", 8.62, 1600000, 70, 11, 2400000, 92000, ["Action", "Fantasy", "Supernatural"], ["MAPPA"]),
    (31964, "My Hero Academia", "TV", "Manga", 13, "Finished Airing", 7.88, 1800000, 800, 6, 2900000, 54000, ["Action", "Supernatural"], ["Bones"]),
    (44511, "Chainsaw Man", "TV", "Manga", 12, "Finished Airing", 8.52, 1200000, 105, 22, 1950000, 78000, ["Action", "Fantasy", "Supernatural"], ["MAPPA"]),
    (52299, "Solo Leveling", "TV", "Web webtoon", 12, "Finished Airing", 8.35, 750000, 190, 35, 1250000, 48000, ["Action", "Fantasy"], ["A-1 Pictures"]),
    (11757, "Sword Art Online", "TV", "Light novel", 25, "Finished Airing", 7.20, 2100000, 2900, 5, 3050000, 71000, ["Action", "Adventure", "Fantasy"], ["A-1 Pictures"]),
    (22319, "Tokyo Ghoul", "TV", "Manga", 12, "Finished Airing", 7.79, 2300000, 1100, 9, 2980000, 93000, ["Action", "Horror", "Psychological"], ["Studio Pierrot"]),
    (6702, "Fairy Tail", "TV", "Manga", 175, "Finished Airing", 7.58, 1350000, 1600, 25, 2100000, 58000, ["Action", "Adventure", "Fantasy"], ["A-1 Pictures"]),
    (30694, "Dragon Ball Super", "TV", "Manga", 131, "Finished Airing", 7.42, 950000, 2100, 78, 1450000, 42000, ["Action", "Adventure", "Fantasy"], ["Toei Animation"]),
    (19, "Monster", "TV", "Manga", 74, "Finished Airing", 8.89, 450000, 24, 140, 1050000, 52000, ["Drama", "Mystery", "Psychological", "Thriller"], ["Madhouse"]),
    (205, "Samurai Champloo", "TV", "Original", 26, "Finished Airing", 8.40, 620000, 180, 110, 1150000, 48000, ["Action", "Adventure", "Comedy"], ["Manglobe"]),
    (199, "Sen to Chihiro no Kamikakushi (Spirited Away)", "Movie", "Original", 1, "Finished Airing", 8.78, 1200000, 32, 42, 1750000, 31000, ["Adventure", "Award Winning", "Supernatural"], ["Studio Ghibli"]),
    (37521, "Vinland Saga", "TV", "Manga", 24, "Finished Airing", 8.73, 850000, 42, 85, 1400000, 61000, ["Action", "Adventure", "Drama", "Historical"], ["Wit Studio"]),
]

def generate_full_mal_catalogue(total_anime=2500, total_users=500, total_ratings=12500):
    print(f"🚀 Generating & Loading Full MAL Catalogue with Black Clover ({total_anime} Anime, {total_users} Users)...")
    
    random.seed(42)
    anime_records = []
    
    for aid, title, ftype, source, eps, status, score, scored_by, rank, pop, mem, fav, g_list, s_list in FAMOUS_ANIME:
        anime_records.append({
            "mal_id": aid,
            "title": title,
            "title_english": title,
            "type": ftype,
            "source": source,
            "episodes": eps,
            "status": status,
            "score": score,
            "scored_by": scored_by,
            "rank": rank,
            "popularity": pop,
            "members": mem,
            "favorites": fav,
            "synopsis": f"{title} is an acclaimed anime series.",
            "genres": json.dumps([{"mal_id": i+1, "name": g} for i, g in enumerate(g_list)]),
            "studios": json.dumps([{"mal_id": i+1, "name": s} for i, s in enumerate(s_list)]),
        })
        
    existing_ids = {a["mal_id"] for a in anime_records}
    next_id = 30
    
    adjectives = ["Chronicles of", "Legend of", "Reborn in", "Tales of", "Rise of", "Shadow of", "Fate of", "Echoes of", "Kingdom of", "Infinite", "Cyber", "Eternal", "Zero", "Saga of", "Overlord", "Beyond"]
    nouns = ["Valhalla", "Aether", "Eclipse", "Horizon", "Starlight", "Genesis", "Destiny", "Phantom", "Abyss", "Vanguard", "Titan", "Specter", "Frontier", "Chronos", "Apex", "Paradox"]
    
    for _ in range(total_anime - len(anime_records)):
        while next_id in existing_ids:
            next_id += 1
        existing_ids.add(next_id)
        
        t_name = f"{random.choice(adjectives)} {random.choice(nouns)}"
        g_sample = random.sample(GENRES_LIST, random.randint(1, 4))
        s_sample = random.sample(STUDIOS_LIST, random.randint(1, 2))
        
        score_val = round(min(9.5, max(4.0, random.gauss(6.8, 1.1))), 2)
        scored_by_val = random.randint(500, 600000)
        members_val = scored_by_val + random.randint(1000, 300000)
        
        anime_records.append({
            "mal_id": next_id,
            "title": t_name,
            "title_english": t_name,
            "type": random.choice(FORMATS),
            "source": random.choice(SOURCES),
            "episodes": random.choice([1, 12, 13, 24, 25, 26, 50, 100]),
            "status": random.choice(STATUSES),
            "score": score_val,
            "scored_by": scored_by_val,
            "rank": random.randint(1, 10000),
            "popularity": random.randint(1, 12000),
            "members": members_val,
            "favorites": random.randint(10, 40000),
            "synopsis": f"An epic {g_sample[0].lower()} adventure featuring {t_name}.",
            "genres": json.dumps([{"mal_id": i+1, "name": g} for i, g in enumerate(g_sample)]),
            "studios": json.dumps([{"mal_id": i+1, "name": s} for i, s in enumerate(s_sample)]),
        })
        next_id += 1

    df_anime = pd.DataFrame(anime_records)

    ratings = []
    anime_id_pool = df_anime["mal_id"].tolist()
    
    for user_id in range(1001, 1001 + total_users):
        user_rating_count = random.randint(15, 45)
        user_sampled_anime = random.sample(anime_id_pool, user_rating_count)
        
        for aid in user_sampled_anime:
            true_score = df_anime[df_anime["mal_id"] == aid]["score"].values[0]
            rating_val = min(10, max(1, int(random.gauss(true_score, 1.2))))
            ratings.append({
                "user_id": user_id,
                "anime_id": aid,
                "rating": rating_val,
                "watch_status": "completed",
                "episodes_watched": random.choice([12, 24, 26, 50, 100])
            })
            
    df_ratings = pd.DataFrame(ratings)

    os.makedirs("data/raw", exist_ok=True)
    df_anime.to_csv("data/raw/sample_anime_metadata.csv", index=False)
    df_ratings.to_csv("data/raw/sample_user_ratings.csv", index=False)

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
    user_stats["user_segment"] = user_stats["total_ratings"].apply(lambda c: "power_user" if c >= 25 else "active_user")
    user_stats.to_sql("dim_user", conn, if_exists="replace", index=False)

    df_ratings.to_sql("fact_user_ratings", conn, if_exists="replace", index=False)
    df_fact_stats = df_anime[["mal_id", "score", "scored_by", "rank", "popularity", "members", "favorites"]].copy()
    df_fact_stats["snapshot_date"] = datetime.now().strftime("%Y-%m-%d")
    df_fact_stats.to_sql("fact_anime_stats", conn, if_exists="replace", index=False)

    global_mean = df_anime["score"].mean()
    m_threshold = 50000.0
    df_scorecard = df_anime.copy()
    df_scorecard["bayesian_weighted_score"] = df_scorecard.apply(
        lambda r: ((r["scored_by"] / (r["scored_by"] + m_threshold)) * r["score"]) +
                  ((m_threshold / (r["scored_by"] + m_threshold)) * global_mean),
        axis=1
    )
    df_scorecard.to_sql("agg_anime_scorecard", conn, if_exists="replace", index=False)

    # Similarity Matrix including Black Clover (34572) and top titles
    top_titles = df_anime.head(150)
    sim_records = []
    for _, a1 in top_titles.iterrows():
        for _, a2 in top_titles.iterrows():
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

    print("\n🎉 Full Catalogue Warehouse Population Completed (Black Clover Added)!")

if __name__ == "__main__":
    generate_full_mal_catalogue()

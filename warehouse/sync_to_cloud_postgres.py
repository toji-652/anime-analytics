import os
import sqlite3
import sys

import pandas as pd
from sqlalchemy import create_engine

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

SQLITE_DB_PATH = "warehouse/anime_analytics.db"

def sync_to_cloud_postgres(postgres_url: str):
    """Syncs all warehouse tables from local SQLite DB into a live Cloud PostgreSQL database for Power BI DirectQuery."""
    print("🚀 Syncing Warehouse Tables to Cloud PostgreSQL Instance...")
    print(f"  Target Database URL: {postgres_url.split('@')[-1] if '@' in postgres_url else postgres_url}")
    
    if not os.path.exists(SQLITE_DB_PATH):
        print(f"⚠️ SQLite database not found at {SQLITE_DB_PATH}")
        return
        
    sqlite_conn = sqlite3.connect(SQLITE_DB_PATH)
    engine = create_engine(postgres_url)
    
    tables_to_sync = [
        "dim_anime",
        "dim_genre",
        "dim_studio",
        "bridge_anime_genre",
        "bridge_anime_studio",
        "fact_user_ratings",
        "fact_anime_stats",
        "agg_anime_scorecard",
        "sync_log"
    ]
    
    for tbl in tables_to_sync:
        try:
            df = pd.read_sql_query(f"SELECT * FROM {tbl}", sqlite_conn)
            df.to_sql(tbl, engine, if_exists="replace", index=False)
            print(f"  ✓ Successfully loaded {tbl:25s} -> Cloud Postgres ({len(df):,} rows)")
        except Exception as e:
            print(f"  ⚠️ Error syncing table {tbl}: {e}")
            
    sqlite_conn.close()
    print("\n🎉 Cloud PostgreSQL Database Synchronization Completed!")
    print("👉 You can now connect Power BI Desktop via DirectQuery to this Cloud PostgreSQL Host!")

if __name__ == "__main__":
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("⚠️ No DATABASE_URL environment variable set.")
        print("Usage: DATABASE_URL='postgresql://user:password@host:5432/dbname' python warehouse/sync_to_cloud_postgres.py")
    else:
        sync_to_cloud_postgres(db_url)

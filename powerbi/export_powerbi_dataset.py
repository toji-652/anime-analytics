import os
import sqlite3
import pandas as pd

DB_PATH = "warehouse/anime_analytics.db"
OUTPUT_DIR = "powerbi/data"

def export_powerbi_tables():
    """Exports SQLite warehouse tables into clean CSV files formatted for 1-click Power BI import."""
    print("📊 Exporting Power BI Data Model Tables from Warehouse...")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    if not os.path.exists(DB_PATH):
        print(f"⚠️ Database not found at {DB_PATH}")
        return
        
    conn = sqlite3.connect(DB_PATH)
    
    tables_to_export = [
        ("dim_anime", "powerbi_dim_anime.csv"),
        ("dim_genre", "powerbi_dim_genre.csv"),
        ("dim_studio", "powerbi_dim_studio.csv"),
        ("bridge_anime_genre", "powerbi_bridge_anime_genre.csv"),
        ("bridge_anime_studio", "powerbi_bridge_anime_studio.csv"),
        ("agg_anime_scorecard", "powerbi_agg_anime_scorecard.csv"),
        ("fact_user_ratings", "powerbi_fact_user_ratings.csv"),
        ("fact_anime_stats", "powerbi_fact_anime_stats.csv"),
    ]
    
    for tbl, filename in tables_to_export:
        try:
            df = pd.read_sql_query(f"SELECT * FROM {tbl}", conn)
            out_path = os.path.join(OUTPUT_DIR, filename)
            df.to_csv(out_path, index=False)
            print(f"  ✓ Exported {tbl:25s} -> {out_path} ({len(df):,} rows)")
        except Exception as e:
            print(f"  ⚠️ Error exporting {tbl}: {e}")
            
    conn.close()
    print("\n✅ Power BI Data Model Export Completed Successfully!")

if __name__ == "__main__":
    export_powerbi_tables()

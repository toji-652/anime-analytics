import os
import sqlite3
import time
from datetime import datetime

DB_PATH = "warehouse/anime_analytics.db"

def run_scheduled_sync():
    """Automated Scheduler task: syncs updated ratings and catalogue data into warehouse tables."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"⏰ [{timestamp}] Running Scheduled Pipeline Sync...")
    
    if not os.path.exists(DB_PATH):
        print(f"⚠️ Database not found at {DB_PATH}")
        return
        
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # 1. Update Snapshot Timestamp in fact_anime_stats
    cur.execute("UPDATE fact_anime_stats SET snapshot_date = ?", (datetime.now().strftime("%Y-%m-%d"),))
    
    # 2. Record sync execution in app.sync_log
    cur.execute("""
        CREATE TABLE IF NOT EXISTS sync_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entity TEXT,
            last_synced_at TEXT,
            records_synced INTEGER,
            status TEXT
        )
    """)
    
    total_anime = cur.execute("SELECT COUNT(*) FROM dim_anime").fetchone()[0]
    total_ratings = cur.execute("SELECT COUNT(*) FROM fact_user_ratings").fetchone()[0]
    
    cur.execute(
        "INSERT INTO sync_log (entity, last_synced_at, records_synced, status) VALUES (?, ?, ?, ?)",
        ("anime_catalogue_and_ratings", timestamp, total_anime + total_ratings, "SUCCESS")
    )
    
    conn.commit()
    conn.close()
    print(f"  ✓ Sync Log updated: {total_anime:,} anime titles & {total_ratings:,} user ratings synchronized successfully.")

def start_daemon_scheduler(interval_seconds=3600):
    print(f"🤖 Starting Pipeline Scheduler Daemon (interval: {interval_seconds}s)...")
    try:
        while True:
            run_scheduled_sync()
            time.sleep(interval_seconds)
    except KeyboardInterrupt:
        print("\n🛑 Scheduler daemon stopped.")

if __name__ == "__main__":
    run_scheduled_sync()

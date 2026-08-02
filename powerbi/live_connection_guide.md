# Live Connection & DirectQuery Guide for Power BI Desktop

This guide explains how to connect **Power BI Desktop** directly to your live database using **DirectQuery** so that whenever data updates in your warehouse, Power BI reflects the changes in real-time without importing static CSVs.

---

## ⚡ Option 1: Live Connection via PostgreSQL DirectQuery (Recommended for Cloud & Production)

When using PostgreSQL, Power BI supports **DirectQuery mode**. In DirectQuery mode, Power BI does **not** store data locally in the `.pbix` file. Every time a user opens the report or changes a slicer, Power BI executes live SQL queries directly against PostgreSQL!

### Step-by-Step Setup:
1. Open **Power BI Desktop**.
2. Click **Get Data** $\rightarrow$ **PostgreSQL database**.
3. In the connection dialog, enter:
   - **Server:** `localhost:5432` (or your cloud PostgreSQL host, e.g., `db.xxx.supabase.co` / `xxx.neon.tech`)
   - **Database:** `anime_analytics`
   - **Data Connectivity Mode:** Select **DirectQuery** ⚡ (instead of Import).
4. Click **OK**.
5. Enter credentials:
   - **User:** `postgres`
   - **Password:** `postgres` (or your cloud DB password)
6. In the Navigator window, select your dimensional star schema tables and marts:
   - `dim_anime`
   - `dim_genre`
   - `dim_studio`
   - `bridge_anime_genre`
   - `bridge_anime_studio`
   - `fact_user_ratings`
   - `agg_anime_scorecard`
7. Click **Load**.

👉 **Result:** Power BI is now connected **LIVE** to PostgreSQL! When new ratings or anime titles are inserted via Airflow or Python scripts, Power BI visuals refresh immediately!

---

## 🔌 Option 2: Live Connection to Local SQLite Database via ODBC

If you are running the project locally with the SQLite database file (`warehouse/anime_analytics.db`), you can connect Power BI directly via ODBC:

### Step-by-Step Setup:
1. **Install SQLite ODBC Driver:**
   - Download & install the free **SQLite3 ODBC Driver** (e.g. `sqlite3odbc.exe` / `sqlite3odbc_w64.exe` from `http://www.ch-werner.de/sqliteodbc/`).
2. **Create Windows DSN (Data Source Name):**
   - Open **ODBC Data Source Administrator** (64-bit) on your machine.
   - Click **Add** under System DSN $\rightarrow$ Select **SQLite3 ODBC Driver**.
   - Data Source Name: `AnimeAnalyticsSQLite`
   - Database Name: Select `/path/to/warehouse/anime_analytics.db`
   - Click **OK**.
3. **Connect Power BI via ODBC:**
   - Open Power BI Desktop $\rightarrow$ **Get Data** $\rightarrow$ **ODBC**.
   - Select `AnimeAnalyticsSQLite` from the DSN dropdown.
   - Click **OK** $\rightarrow$ Select tables $\rightarrow$ Click **Load** (or click **Refresh** anytime to fetch live updates!).

---

## ⏱️ Option 3: Automatic Scheduled Refresh in Power BI Service

If you publish your report to **Power BI Service** (app.powerbi.com):
1. Install **Power BI On-Premises Data Gateway** (or Cloud Direct Query Gateway).
2. Set **Scheduled Refresh** frequency to **Hourly** or **Daily**.
3. Power BI Service will automatically trigger SQL queries and update dashboard visuals automatically in the background!

# Power BI Desktop Setup Guide & Report Instructions

This guide provides step-by-step instructions to load the exported warehouse CSV datasets into **Power BI Desktop**, set up the Star Schema data model, configure DAX measures, and design the 4-page report.

---

## 📁 1. Load Data Files into Power BI Desktop

1. Open **Power BI Desktop**.
2. Click **Get Data** $\rightarrow$ **Text/CSV**.
3. Navigate to `powerbi/data/` inside this project directory:
   - Select `powerbi_dim_anime.csv`
   - Select `powerbi_dim_genre.csv`
   - Select `powerbi_dim_studio.csv`
   - Select `powerbi_bridge_anime_genre.csv`
   - Select `powerbi_bridge_anime_studio.csv`
   - Select `powerbi_agg_anime_scorecard.csv`
   - Select `powerbi_fact_user_ratings.csv`
   - Select `powerbi_fact_anime_stats.csv`
4. Click **Load**.

---

## 🔗 2. Configure Star Schema Data Relationships

Go to **Model View** in Power BI Desktop and create the following relationships:

| From Table | From Column | To Table | To Column | Cardinality | Cross Filter |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `powerbi_dim_anime` | `mal_id` | `powerbi_bridge_anime_genre` | `anime_id` | `1 to Many (*)` | Single |
| `powerbi_dim_genre` | `genre_id` | `powerbi_bridge_anime_genre` | `genre_id` | `1 to Many (*)` | Single |
| `powerbi_dim_anime` | `mal_id` | `powerbi_bridge_anime_studio` | `anime_id` | `1 to Many (*)` | Single |
| `powerbi_dim_studio` | `studio_id` | `powerbi_bridge_anime_studio` | `studio_id` | `1 to Many (*)` | Single |
| `powerbi_dim_anime` | `mal_id` | `powerbi_fact_user_ratings` | `anime_id` | `1 to Many (*)` | Single |
| `powerbi_dim_anime` | `mal_id` | `powerbi_agg_anime_scorecard` | `mal_id` | `1 to 1` | Both |

---

## 🧮 3. Create DAX Measures Table (`_Measures`)

1. Click **Enter Data** on the Home tab. Name the table `_Measures`.
2. Right-click `_Measures` $\rightarrow$ **New Measure** and add the following DAX measures:

### Total Titles
```dax
Total Titles = COUNT(powerbi_dim_anime[mal_id])
```

### Average MAL Score
```dax
Average MAL Score = AVERAGE(powerbi_dim_anime[score])
```

### Total Members
```dax
Total Members = SUM(powerbi_dim_anime[members])
```

### Total Ingested Ratings
```dax
Total Ratings = COUNT(powerbi_fact_user_ratings[rating])
```

### Dynamic Bayesian Score
```dax
Dynamic Bayesian Score = 
VAR GlobalMean = CALCULATE(AVERAGE(powerbi_dim_anime[score]), ALL(powerbi_dim_anime))
VAR VoteThreshold = 50000
VAR ScoredBy = SUM(powerbi_dim_anime[scored_by])
VAR Score = AVERAGE(powerbi_dim_anime[score])
RETURN
    IF(
        ISBLANK(Score),
        BLANK(),
        ((ScoredBy / (ScoredBy + VoteThreshold)) * Score) + ((VoteThreshold / (ScoredBy + VoteThreshold)) * GlobalMean)
    )
```

---

## 📊 4. Design the 4 Report Pages

### Page 1: Catalogue Overview
- **Header:** 4 Card Visuals (`Total Titles`, `Total Ratings`, `Average MAL Score`, `Dynamic Bayesian Score`).
- **Main Chart:** Line Chart showing Titles Released per Year (`year` on X-axis, `Total Titles` on Y-axis).
- **Visual 2:** Clustered Column Chart for Format Split (`type` on X-axis, `Total Titles` on Y-axis).
- **Visual 3:** Table/Matrix Visual (`title`, `type`, `score`, `members`, `favorites`).

### Page 2: Studio Performance
- **Visual 1:** Studio Leaderboard Matrix (`studio_name`, `Total Titles`, `Average MAL Score`, `Total Members`).
- **Visual 2:** Dual-Axis Line & Stacked Column Chart (Column = `Total Titles`, Line = `Average MAL Score`).

### Page 3: Genre Analysis & Trends
- **Visual 1:** Bar Chart of Top Genres (`genre_name` on Y-axis, `Total Titles` on X-axis).
- **Visual 2:** Scatter Plot (`Total Titles` on X-axis, `Average MAL Score` on Y-axis, bubble = `genre_name`).

### Page 4: Hidden Gems & High-Rated Analytics
- **Visual 1:** High-Rated Hidden Gems Matrix (Filter: `Score >= 7.5` and `Members <= 100,000`).
- **Visual 2:** Scorecard Ranking Table sorted by `Dynamic Bayesian Score`.

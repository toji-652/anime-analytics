# Power BI Report Page Blueprint

## Page 1: Catalogue Overview
- **Header:** KPI Cards (`Total Titles`, `Total Ratings`, `Average Score`, `Bayesian Score`)
- **Main Chart:** Line Chart showing Titles Released per Year (Trend)
- **Visual 2:** Score Distribution Histogram (bins: 1.0 to 10.0)
- **Visual 3:** Donut Chart of Format Split (`TV`, `Movie`, `OVA`, `ONA`, `Special`)

## Page 2: Studio Performance
- **Visual 1:** Studio Leaderboard Matrix (`Studio Name`, `Total Titles`, `Avg MAL Score`, `Avg Bayesian Score`, `Total Members`)
- **Visual 2:** Studio Output & Quality over Time (Dual-Axis Combo Chart: Bar = Title Count, Line = Avg Score)
- **Visual 3:** Studio × Genre Specialization Matrix

## Page 3: Genre Trends
- **Visual 1:** Genre Popularity Over Time (Stacked Area Chart of Genre Share %)
- **Visual 2:** Score vs. Volume Scatter Plot per Genre (X = Total Titles, Y = Avg Score)
- **Visual 3:** Genre Co-occurrence Matrix / Heatmap (`marts.agg_genre_cooccurrence`)

## Page 4: Hidden Gems & Seasonal Rankings
- **Visual 1:** Score vs. Popularity Scatter Plot with Highlighted "Hidden Gems" Quadrant (`Score >= 7.8`, `Members <= 50,000`)
- **Visual 2:** Seasonal Rankings Bar Chart (Best / Worst Seasons by Avg Score)
- **Visual 3:** Seasonal Competition Density (Title count airing per season)

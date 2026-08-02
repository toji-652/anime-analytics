# PRD — Anime Analytics & Recommendation Platform

**Project codename:** `anime-analytics`
**Doc type:** Product Requirements Document
**Owner:** <your name>
**Status:** Draft v1.0

---

## 1. Problem statement

Anime catalogue and rating data is abundant but scattered and structurally awkward:

- Metadata lives behind APIs with rate limits and nested, multi-valued fields (genres, studios, producers are arrays, not columns)
- Bulk user-rating data exists only as static dumps, not via API
- Nobody publishes a clean, queryable historical view of how genre popularity, studio output quality, or seasonal competition have shifted over time
- Recommendation on public sites is opaque — "similar anime" with no explanation of why

This makes otherwise interesting questions hard to answer:

- Which studios consistently outperform, and has that changed over the last decade?
- Which genres are rising or declining, and does score follow popularity or diverge from it?
- Which seasons were unusually strong or weak, and which shows were crowded out?
- What are the "hidden gems" — high score, low popularity?
- Given an anime I liked, what should I watch next, and why?

## 2. Goal

Build an end-to-end platform that blends a static bulk historical load with incremental API-based updates, models the result dimensionally (including a proper many-to-many genre relationship), serves a Power BI analytics layer, and exposes a recommendation API.

## 3. Non-goals

- Scraping content, images, or video — metadata and ratings only
- Real-time recommendations at scale (batch-computed similarity is sufficient)
- User accounts / personalization beyond "given anime X, recommend Y"
- Cloud deployment (runs locally via Docker)

## 4. Target users & use cases

| Persona | Use case | Key question |
|---|---|---|
| Viewer | Find what to watch next | I liked *X*, what's similar and actually good? |
| Industry analyst | Studio performance tracking | Is Studio A's output quality declining? |
| Content strategist | Genre trend analysis | Is isekai saturating? What's rising? |
| Data enthusiast | Hidden gem discovery | What's underrated relative to its score? |

## 5. Success criteria

**Functional**
- Historical load covers the full bulk ratings dataset plus complete anime metadata
- Incremental job keeps metadata fresh on a schedule without re-pulling everything
- Genre/studio many-to-many correctly modeled via bridge tables — no comma-separated strings in the warehouse
- Power BI report answers all five questions in §1
- Recommendation API returns 10 results in under 500ms

**Quality**
- Zero duplicate ratings at (user, anime) grain
- Every anime in the fact table resolves to a row in `dim_anime` (referential integrity enforced by test)
- Recommendation quality: precision@10 measured against a held-out set of user ratings; documented baseline vs. model

**Portfolio**
- `docker compose up` brings up the whole stack
- Live demo path: type an anime title → get explained recommendations
- README with architecture diagram and design rationale

## 6. Scope — v1 deliverables

1. **Bulk loader** — one-time ingestion of the static ratings + metadata dump
2. **Incremental API service** — scheduled Jikan API pulls for new/updated titles
3. **Processing layer** — JSON flattening, array explosion, dedupe
4. **Dimensional warehouse** — star schema with bridge tables, built and tested via dbt
5. **Aggregate marts** — pre-computed tables for BI
6. **Orchestration** — Airflow DAGs for both the bulk and incremental paths
7. **Power BI report** — 4 pages (Overview, Studios, Genres, Hidden Gems)
8. **Recommendation engine** — collaborative filtering + content-based hybrid, served via FastAPI with a Streamlit demo UI

## 7. Report requirements (Power BI)

**Page 1 — Catalogue Overview**
- KPI cards: total titles, total ratings, average score, titles airing
- Titles released per year, trend
- Score distribution histogram
- Format split (TV / Movie / OVA / ONA / Special)

**Page 2 — Studio Performance**
- Studio leaderboard: avg score, title count, total members, weighted score
- Studio output and quality over time, dual-axis
- Studio × genre specialization matrix
- Drill-through to a studio's full title list

**Page 3 — Genre Trends**
- Genre popularity over time, stacked area (share of titles per year)
- Score vs. volume scatter per genre
- Genre co-occurrence heatmap (which genres pair together)

**Page 4 — Hidden Gems & Seasons**
- Score vs. popularity scatter with a "hidden gem" quadrant highlighted
- Seasonal rankings: best/worst seasons by average score
- Seasonal competition view: how many strong titles aired simultaneously

**DAX measures required:** weighted average score (Bayesian-adjusted, so a 10.0 from 12 raters doesn't outrank a 9.1 from 400k), score percentile rank, YoY title-count growth, genre share %, popularity-to-score ratio.

> The Bayesian-weighted score is deliberately called out — plain `AVERAGE(score)` produces a nonsense leaderboard dominated by obscure titles, and explaining that trade-off is a strong interview talking point.

## 8. Constraints

- **Cost:** ₹0 / $0. All components free and local.
- **Hardware:** must run on a 16GB RAM laptop.
- **API politeness:** Jikan is a free community-run service — respect its published rate limits strictly, cache aggressively, and never re-pull data already held.
- **Power BI:** Desktop only. Deliverable is the `.pbix` plus exported screenshots.

## 9. Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Jikan rate limits slow incremental sync | Long runtimes | Only sync titles changed since last watermark; batch and cache; make the DAG resumable |
| Bulk dataset is stale | Recent titles missing | Incremental API path exists precisely to close this gap; document the seam |
| Ratings dataset is very large | Memory pressure | Process in Spark, never load fully into pandas |
| Cold-start for new/obscure titles in collaborative filtering | Poor recommendations | Hybrid with content-based (genre/studio/synopsis similarity) fallback |
| Genre arrays modeled lazily | Broken aggregations | Bridge table is a hard requirement, enforced by schema tests |

## 10. Open questions

- Which bulk dataset version has the best ratings coverage and cleanest schema?
- Is synopsis text available and usable for TF-IDF/embedding content similarity?
- Should recommendations weight recency (newer titles surfaced more)?

## 11. Future scope (v2+)

- Sentiment analysis on review text
- Embedding-based semantic search over synopses
- Airing-season forecast: predict a new title's score from pre-release metadata
- A/B comparison of recommendation strategies with an offline evaluation harness

import os

tickets_data = [
    {
        "id": "0001",
        "slug": "0001-scaffold-repo-and-docker-compose.md",
        "title": "Scaffold repository structure and docker-compose",
        "status": "backlog",
        "role": "devops-agent",
        "depends": [],
        "desc": "Scaffold directory structure per TRD §3 and construct `docker-compose.yml` defining services for PostgreSQL 16, MinIO, Apache Airflow 2.9+, and MLflow with memory constraints (16GB hardware budget).",
        "ac": [
            "Repository directory tree matches TRD §3 structure",
            "docker-compose.yml defines postgres, minio, airflow-webserver, airflow-scheduler, mlflow services",
            "Healthchecks pass for Postgres and MinIO upon `docker compose up`",
            ".env.example includes all environment variables and secrets placeholders"
        ],
        "notes": "TRD §2, §3, §8"
    },
    {
        "id": "0002",
        "slug": "0002-init-database-schemas-and-minio-buckets.md",
        "title": "Initialize PostgreSQL schemas and MinIO buckets",
        "status": "backlog",
        "role": "devops-agent",
        "depends": ["0001"],
        "desc": "Create startup DDL scripts for PostgreSQL (`raw`, `staging`, `marts`, `app` schemas) and automate MinIO bucket creation (`bronze`, `silver`, `gold`).",
        "ac": [
            "Postgres initializes with schemas `raw`, `staging`, `marts`, `app` on first run",
            "MinIO automatically provisions `bronze`, `silver`, and `gold` buckets on boot",
            "Postgres user permissions granted appropriately for dbt and Airflow"
        ],
        "notes": "TRD §1, §4"
    },
    {
        "id": "0003",
        "slug": "0003-implement-bulk-loader-script.md",
        "title": "Implement static bulk loader for historical dump",
        "status": "backlog",
        "role": "backend-developer",
        "depends": ["0002"],
        "desc": "Write `ingestion/bulk_loader.py` to ingest the static MyAnimeList/Kaggle bulk ratings and metadata CSV/Parquet dump into MinIO Bronze layer.",
        "ac": [
            "Bulk dataset ingested and partitioned into MinIO `bronze/ratings/` and `bronze/metadata/`",
            "Includes schema validation and log reporting of row counts loaded",
            "Memory-friendly execution using chunked reading or pyarrow"
        ],
        "notes": "PRD §6 item 1, TRD §5.1"
    },
    {
        "id": "0004",
        "slug": "0004-build-rate-limited-jikan-api-client.md",
        "title": "Build rate-limited Jikan API client with caching",
        "status": "backlog",
        "role": "backend-developer",
        "depends": ["0001"],
        "desc": "Develop `ingestion/jikan_client.py` using `httpx` to interact with Jikan API v4 respecting published rate limits (3 req/sec), featuring token bucket limiter, exponential backoff on 429/5xx, and response caching.",
        "ac": [
            "Enforces published rate limit ceiling strictly via token bucket limiter",
            "Retries with exponential backoff + jitter on 429 and 5xx response codes",
            "Caches API responses locally by endpoint + params to avoid redundant hits",
            "Logs HTTP 404 (deleted titles) without retrying infinitely"
        ],
        "notes": "PRD §8, TRD §5.1"
    },
    {
        "id": "0005",
        "slug": "0005-build-watermark-based-incremental-sync.md",
        "title": "Build watermark-based incremental sync module",
        "status": "backlog",
        "role": "backend-developer",
        "depends": ["0002", "0004"],
        "desc": "Implement `ingestion/incremental_sync.py` maintaining a `sync_log` watermark table in Postgres to pull new and updated titles from Jikan API into MinIO Bronze.",
        "ac": [
            "`sync_log` table created in Postgres tracking `entity`, `last_synced_at`, `last_mal_id`, `status`",
            "Sync pulls only titles updated since last watermark date",
            "Idempotent: re-running for the same window generates zero duplicates",
            "Appends raw JSON responses to MinIO Bronze bucket under date partition"
        ],
        "notes": "PRD §6 item 2, TRD §5.2"
    },
    {
        "id": "0006",
        "slug": "0006-implement-pyspark-processing-jobs.md",
        "title": "Implement PySpark jobs for metadata and ratings",
        "status": "backlog",
        "role": "backend-developer",
        "depends": ["0003", "0005"],
        "desc": "Implement PySpark 3.5 processing jobs (`processing/spark_jobs/flatten_metadata.py` and `clean_ratings.py`) to explode nested arrays (genres, studios), hash user IDs, deduplicate ratings, and write Parquet Silver layer.",
        "ac": [
            "`flatten_metadata.py` reads JSON with explicit schema and explodes genres/studios into `silver/`",
            "`clean_ratings.py` filters invalid scores (<1 or >10), dedupes `(user_id, anime_id)`, and hashes user IDs",
            "PySpark memory configured within 4GB driver budget",
            "Parquet files written cleanly to MinIO `silver/`"
        ],
        "notes": "TRD §5.3"
    },
    {
        "id": "0007",
        "slug": "0007-setup-dbt-project-seeds-and-staging.md",
        "title": "Setup dbt project, seeds, and staging models",
        "status": "backlog",
        "role": "backend-developer",
        "depends": ["0006"],
        "desc": "Initialize dbt project in `warehouse/`, add seeds (`genre_mapping.csv`, `season_calendar.csv`), and create staging models over PostgreSQL tables.",
        "ac": [
            "`dbt_project.yml` and `profiles.yml` configured for PostgreSQL",
            "`dbt seed` loads `genre_mapping.csv` and `season_calendar.csv` successfully",
            "Staging models (`stg_anime`, `stg_ratings`, `stg_studios`, `stg_genres`) clean and rename raw columns"
        ],
        "notes": "TRD §4, §5.4"
    },
    {
        "id": "0008",
        "slug": "0008-build-dbt-core-star-schema-and-bridges.md",
        "title": "Build dbt core star schema dimensions and bridge tables",
        "status": "backlog",
        "role": "backend-developer",
        "depends": ["0007"],
        "desc": "Create core dbt models: `dim_anime` (SCD2 snapshot), `dim_studio`, `dim_genre`, `dim_user`, `dim_date`, `fact_user_ratings`, `fact_anime_stats`, and bridge tables `bridge_anime_genre` & `bridge_anime_studio`.",
        "ac": [
            "`dim_anime` implements SCD2 snapshot functionality for title/status history",
            "`bridge_anime_genre` and `bridge_anime_studio` map many-to-many relationships without array strings",
            "`fact_user_ratings` materialized incrementally with natural key `(user_key, anime_key)`",
            "`fact_anime_stats` captures time-series metrics per snapshot date"
        ],
        "notes": "PRD §6 item 4, TRD §4"
    },
    {
        "id": "0009",
        "slug": "0009-build-dbt-aggregate-marts-with-bayesian-scorecard.md",
        "title": "Build dbt aggregate marts with Bayesian scorecard",
        "status": "backlog",
        "role": "backend-developer",
        "depends": ["0008"],
        "desc": "Build analytical aggregate marts (`agg_studio_performance`, `agg_genre_trends`, `agg_genre_cooccurrence`, `agg_seasonal_rankings`, `agg_anime_scorecard`, `agg_hidden_gems`), calculating Bayesian-weighted scores in dbt.",
        "ac": [
            "Bayesian weighted score computed accurately: `(v / (v + m)) * R + (m / (v + m)) * C`",
            "`agg_genre_cooccurrence` models genre pairing frequencies for heatmaps",
            "`agg_hidden_gems` isolates high-score, low-popularity titles",
            "Aggregate tables pre-resolve bridge fan-out so Power BI direct queries do not double-count"
        ],
        "notes": "PRD §7, TRD §4"
    },
    {
        "id": "0010",
        "slug": "0010-build-dbt-test-suite-and-referential-integrity.md",
        "title": "Build dbt test suite and referential integrity assertions",
        "status": "backlog",
        "role": "qa-engineer",
        "depends": ["0009"],
        "desc": "Define dbt schema tests (`unique`, `not_null`, `relationships`, `accepted_values`, `accepted_range`) and singular custom tests to ensure referential integrity across star schema and bridges.",
        "ac": [
            "All surrogate keys pass `unique` and `not_null` tests",
            "Every `anime_key` in `fact_user_ratings` resolves to `dim_anime`",
            "Singular test confirms no anime in warehouse has zero genre bridge rows",
            "Range tests enforce score boundaries (1-10)"
        ],
        "notes": "PRD §5, TRD §5.4"
    },
    {
        "id": "0011",
        "slug": "0011-develop-als-collaborative-filtering-pipeline.md",
        "title": "Develop ALS collaborative filtering pipeline with MLflow",
        "status": "backlog",
        "role": "backend-developer",
        "depends": ["0008"],
        "desc": "Develop `ml/train_collaborative.py` using `implicit` library ALS matrix factorization on user-anime interaction matrices, logging parameters and metrics to MLflow.",
        "ac": [
            "ALS matrix factorization model trains on user x anime interaction matrix",
            "Hyperparameters (factors, regularization, iterations) logged to MLflow",
            "Model artifacts saved cleanly in `ml/artifacts/`"
        ],
        "notes": "TRD §5.5"
    },
    {
        "id": "0012",
        "slug": "0012-develop-tfidf-content-based-recommendation.md",
        "title": "Develop TF-IDF content-based recommendation model",
        "status": "backlog",
        "role": "backend-developer",
        "depends": ["0008"],
        "desc": "Develop `ml/train_content.py` using TF-IDF over anime synopses combined with one-hot encoded genres, studios, and source types to build cosine similarity matrices.",
        "ac": [
            "TF-IDF vectorizer built on `synopsis` combined with genre and studio metadata",
            "Cosine similarity matrix computed for all catalogue items",
            "Cold-start handling verified for titles with 0 user ratings"
        ],
        "notes": "TRD §5.5"
    },
    {
        "id": "0013",
        "slug": "0013-build-hybrid-recommender-and-evaluation-harness.md",
        "title": "Build hybrid recommender and evaluation harness",
        "status": "backlog",
        "role": "backend-developer",
        "depends": ["0011", "0012"],
        "desc": "Implement `ml/hybrid.py` blending ALS collaborative and TF-IDF content scores, and build `ml/evaluate.py` testing precision@10, recall@10, and catalogue coverage against a popularity baseline.",
        "ac": [
            "Hybrid model dynamically blends collaborative and content scores based on rating counts",
            "`ml/evaluate.py` measures precision@10, recall@10, and coverage on held-out user test set",
            "Model evaluation gate verifies hybrid recommender outperforms popularity baseline"
        ],
        "notes": "PRD §5, TRD §5.5"
    },
    {
        "id": "0014",
        "slug": "0014-implement-precomputed-similarity-exporter.md",
        "title": "Implement precomputed similarity matrix exporter",
        "status": "backlog",
        "role": "backend-developer",
        "depends": ["0013"],
        "desc": "Write `ml/export_similarity.py` to write top-50 precomputed recommendations per anime into PostgreSQL `app.recommendation_similarity` table for fast API lookup.",
        "ac": [
            "Top-50 similar titles per anime written to `app.recommendation_similarity` table",
            "Includes recommendation score and explanation metadata (shared genres, studio match)",
            "Database table indexed on `anime_id` for sub-50ms query lookups"
        ],
        "notes": "TRD §5.5"
    },
    {
        "id": "0015",
        "slug": "0015-develop-fastapi-backend-recommendation-service.md",
        "title": "Develop FastAPI backend recommendation service",
        "status": "backlog",
        "role": "backend-developer",
        "depends": ["0014"],
        "desc": "Implement FastAPI application in `api/main.py` providing `/health`, `/anime/search`, `/recommend/{mal_id}`, and `/recommend/explain/{mal_id}/{rec_id}` endpoints.",
        "ac": [
            "`GET /health` returns service status",
            "`GET /anime/search?q=` provides fast title autocomplete",
            "`GET /recommend/{mal_id}?n=10` returns top 10 similar titles in <500ms p95 latency",
            "`GET /recommend/explain/{mal_id}/{rec_id}` explains why title was recommended"
        ],
        "notes": "PRD §5, TRD §5.6"
    },
    {
        "id": "0016",
        "slug": "0016-build-streamlit-web-ui-for-recommendation-demo.md",
        "title": "Build Streamlit Web UI for recommendation demo",
        "status": "backlog",
        "role": "frontend-developer",
        "depends": ["0015"],
        "desc": "Build single-page Streamlit application (`ui/streamlit_app.py`) allowing users to search an anime title, view top recommendations as UI cards, and inspect recommendation explanations.",
        "ac": [
            "Search bar with live title autocomplete calling FastAPI backend",
            "Displays top 10 recommendations as clean visual cards with title, score, and genres",
            "Expandable explainability section showing why each anime was recommended",
            "Responsive layout tested on desktop browser"
        ],
        "notes": "PRD §6 item 8, TRD §5.7"
    },
    {
        "id": "0017",
        "slug": "0017-build-unit-and-integration-pytest-suite.md",
        "title": "Build unit and integration pytest suite",
        "status": "backlog",
        "role": "qa-engineer",
        "depends": ["0004", "0006", "0015"],
        "desc": "Implement pytest test suite covering Jikan client rate limiting and retries, PySpark transformation functions, Bayesian score math, and FastAPI endpoint contracts.",
        "ac": [
            "Unit tests for Jikan rate limiter and retry backoff pass with mock HTTP client",
            "PySpark metadata explosion tested on sample JSON fixture",
            "FastAPI `TestClient` tests verify all endpoint responses and 404 error handling",
            "Pytest runs cleanly via standard command `pytest`"
        ],
        "notes": "TRD §7"
    },
    {
        "id": "0018",
        "slug": "0018-design-powerbi-report-layout-and-dax-library.md",
        "title": "Design Power BI report layout and DAX measure library",
        "status": "backlog",
        "role": "business-analyst",
        "depends": ["0009"],
        "desc": "Specify Power BI report file structure (`powerbi/anime_analytics.pbix`) and DAX measures across 4 pages: Overview, Studio Performance, Genre Trends, and Hidden Gems.",
        "ac": [
            "DAX measures defined: Bayesian weighted score, score percentile rank, YoY title growth, genre share %",
            "Page 1: Catalogue overview with KPI cards, release trend, score histogram, format split",
            "Page 2: Studio leaderboard, output vs quality dual-axis, genre specialization matrix",
            "Page 3: Genre popularity stacked area, score vs volume scatter, co-occurrence heatmap",
            "Page 4: Hidden gems quadrant scatter and seasonal competition rankings"
        ],
        "notes": "PRD §7, TRD §5.8"
    },
    {
        "id": "0019",
        "slug": "0019-implement-airflow-dags-for-bulk-incremental-ml.md",
        "title": "Implement Airflow DAGs for bulk, incremental, and ML pipeline",
        "status": "backlog",
        "role": "devops-agent",
        "depends": ["0006", "0009", "0014"],
        "desc": "Construct Apache Airflow DAGs (`anime_bulk_load_dag`, `anime_incremental_dag`, `anime_train_recommender_dag`) enforcing task dependencies and ML baseline validation gates.",
        "ac": [
            "`anime_bulk_load_dag` orchestrates bulk dump -> spark -> dbt seed/run/test",
            "`anime_incremental_dag` scheduled daily for Jikan API fetch -> silver land -> dbt incremental -> stats snapshot",
            "`anime_train_recommender_dag` scheduled weekly for ML extraction -> train -> eval gate -> similarity export",
            "Airflow DAGs parse without errors and execute green in Airflow UI"
        ],
        "notes": "PRD §6 item 6, TRD §6"
    },
    {
        "id": "0020",
        "slug": "0020-configure-github-actions-ci-pipeline.md",
        "title": "Configure GitHub Actions CI pipeline",
        "status": "backlog",
        "role": "devops-agent",
        "depends": ["0017"],
        "desc": "Create `.github/workflows/ci.yml` running code linting (`ruff`), pytest test suites, and dbt manifest parsing on every push and pull request.",
        "ac": [
            "GitHub Actions workflow runs on push to main and PRs",
            "Steps execute `ruff check .`, `pytest`, and `dbt parse`",
            "CI build succeeds and blocks failing PRs"
        ],
        "notes": "TRD §2, §7"
    },
    {
        "id": "0021",
        "slug": "0021-finalize-readme-architecture-docs-and-demo.md",
        "title": "Finalize project README, architecture diagrams, and demo assets",
        "status": "backlog",
        "role": "scrum-master",
        "depends": ["0016", "0018", "0019", "0020"],
        "desc": "Write comprehensive project `README.md` with system architecture diagram, local quickstart guide (`docker compose up`), Power BI screenshots, and Streamlit demo recording.",
        "ac": [
            "README contains high-level architecture diagram and tech stack rationale",
            "Step-by-step setup instructions for running local Docker stack and Streamlit UI",
            "Screenshots of Power BI 4-page report saved in `powerbi/screenshots/`",
            "Definition of Done checklist verified complete"
        ],
        "notes": "PRD §5, TRD §9"
    }
]

tickets_dir = "/Users/griffin652/Projects/switch/anime_analystics/tickets"

for t in tickets_data:
    filepath = os.path.join(tickets_dir, t["slug"])
    depends_str = "[" + ", ".join([f'"{d}"' for d in t["depends"]]) + "]"
    ac_lines = "\n".join([f"- [ ] {ac}" for ac in t["ac"]])
    content = f"""---
id: "{t['id']}"
title: {t['title']}
status: {t['status']}
assigned-role: {t['role']}
assigned-agent: null
depends-on: {depends_str}
created-by: scrum-master
created: 2026-08-02
branch: ticket/{t['id']}-{t['slug'].replace('.md', '').split('-', 1)[1]}
---

## Description
{t['desc']}

## Acceptance Criteria
{ac_lines}

## Notes / Links
- {t['notes']}
"""
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

print(f"Successfully generated {len(tickets_data)} ticket files.")

# TRD — Anime Analytics & Recommendation Platform

**Project codename:** `anime-analytics`
**Doc type:** Technical Requirements Document
**Companion doc:** `anime-analytics-PRD.md`
**Status:** Draft v1.0

---

## 1. Architecture overview

```
┌────────────────────┐     ┌──────────────────┐
│ Bulk dataset dump  │     │ Jikan REST API   │
│ (ratings + meta)   │     │ (incremental)    │
└─────────┬──────────┘     └────────┬─────────┘
          │                         │
          └──────────┬──────────────┘
                     ▼
┌────────────────────────────────────────────┐
│ MinIO — object storage                      │
│  bronze/  raw JSON + CSV, partitioned       │
│  silver/  flattened, deduped Parquet        │
└─────────┬───────────────────────────────────┘
          │ PySpark (local mode)
          ▼
┌────────────────────────────────────────────┐
│ PostgreSQL — data warehouse                 │
│  raw / staging / marts schemas              │
│  star schema + bridge tables                │
└────┬────────────────────────┬───────────────┘
     │ dbt-core               │
     ▼                        ▼
┌──────────────┐     ┌────────────────────────┐
│ Power BI     │     │ Recommender training   │
│ Desktop      │     │ → FastAPI + Streamlit  │
└──────────────┘     └────────────────────────┘

Orchestration: Apache Airflow
Experiment tracking: MLflow
```

## 2. Tech stack

| Layer | Technology | Rationale |
|---|---|---|
| Bulk ingestion | Python 3.11, pandas/pyarrow | One-time CSV → Parquet load |
| API ingestion | Python, `httpx` with retry + rate limiter | Jikan is community-run; politeness is mandatory |
| Object storage | MinIO | S3-compatible, portable to real S3 unchanged |
| Processing | PySpark 3.5 (local mode) | Ratings dataset is tens of millions of rows; array explosion is a natural Spark operation |
| Warehouse | PostgreSQL 16 | Free, good analytical SQL, native Power BI connector |
| Transformation | dbt-core + dbt-postgres | Lineage, tests, docs |
| Orchestration | Airflow 2.9+ | Two DAGs: bulk backfill and incremental sync |
| ML | `implicit` (ALS) or `scikit-surprise`, scikit-learn (TF-IDF) | Collaborative + content hybrid |
| Tracking | MLflow | Params, metrics, model registry |
| Serving | FastAPI + Streamlit | API for the resume, UI for the demo |
| BI | Power BI Desktop | Per PRD |
| CI | GitHub Actions | ruff, pytest, dbt parse |

## 3. Repository structure

```
anime-analytics/
├── docker-compose.yml
├── .env.example
├── README.md
├── docs/
│   ├── PRD.md
│   ├── TRD.md
│   └── architecture.png
├── ingestion/
│   ├── bulk_loader.py        # static dump → bronze
│   ├── jikan_client.py       # rate-limited API client
│   ├── incremental_sync.py   # watermark-based updates
│   └── config.py
├── processing/
│   └── spark_jobs/
│       ├── flatten_metadata.py    # explode genres/studios/producers
│       ├── clean_ratings.py
│       └── build_bridges.py
├── warehouse/                # dbt project
│   ├── dbt_project.yml
│   ├── seeds/
│   │   ├── genre_mapping.csv
│   │   └── season_calendar.csv
│   ├── models/
│   │   ├── staging/
│   │   ├── intermediate/
│   │   └── marts/
│   │       ├── core/
│   │       └── aggregates/
│   └── tests/
├── ml/
│   ├── train_collaborative.py
│   ├── train_content.py
│   ├── hybrid.py
│   ├── evaluate.py           # precision@k, recall@k, coverage
│   └── artifacts/
├── api/
│   ├── main.py               # FastAPI
│   ├── schemas.py
│   └── recommender_service.py
├── ui/
│   └── streamlit_app.py
├── orchestration/
│   └── dags/
│       ├── anime_bulk_load_dag.py
│       ├── anime_incremental_dag.py
│       └── anime_train_recommender_dag.py
├── powerbi/
│   ├── anime_analytics.pbix
│   └── screenshots/
└── tests/
```

## 4. Data model — star schema with bridges

### `fact_user_ratings` (grain: one row per user × anime)

| Column | Type | Notes |
|---|---|---|
| rating_sk | BIGSERIAL | surrogate PK |
| user_key | BIGINT | FK → dim_user |
| anime_key | INT | FK → dim_anime |
| date_key | INT | FK → dim_date (nullable if dump lacks timestamps) |
| score | SMALLINT | 1–10 |
| watch_status | TEXT | completed / watching / dropped / etc. |
| episodes_watched | INT | |
| loaded_at | TIMESTAMP | audit |

Natural key: `(user_key, anime_key)` — must be unique.

### `fact_anime_stats` (grain: one row per anime × snapshot date)

Slowly-changing popularity metrics captured by the incremental sync — this gives the report a *time dimension on popularity*, which the bulk dump alone cannot provide.

| Column | Type |
|---|---|
| anime_key | INT (FK) |
| snapshot_date_key | INT (FK) |
| mal_score | NUMERIC(4,2) |
| scored_by | INT |
| rank | INT |
| popularity_rank | INT |
| members | INT |
| favorites | INT |

### Dimensions

**`dim_anime`** — `anime_key`, `mal_id`, `title`, `title_english`, `title_japanese`, `type` (TV/Movie/OVA/ONA/Special), `source` (manga/light novel/original/game), `episodes`, `duration_minutes`, `status`, `aired_from`, `aired_to`, `season`, `season_year`, `rating_certificate`, `synopsis`, `is_current` + SCD2 columns (`valid_from`, `valid_to`)

**`dim_studio`** — `studio_key`, `mal_studio_id`, `studio_name`, `established_year` (if available)

**`dim_genre`** — `genre_key`, `genre_name`, `genre_type` (genre / theme / demographic — MAL distinguishes these and collapsing them loses information)

**`dim_user`** — `user_key`, `mal_user_id_hash`, `rating_count`, `avg_score_given`, `user_segment` (casual / active / power, derived from rating volume)

**`dim_date`** — day grain: `date_key`, `full_date`, `year`, `quarter`, `month`, `anime_season` (Winter/Spring/Summer/Fall), `season_year`

### Bridge tables (the modeling centerpiece)

**`bridge_anime_genre`** — `anime_key`, `genre_key`, `is_primary_genre`
**`bridge_anime_studio`** — `anime_key`, `studio_key`, `role` (studio / producer / licensor)

> These exist because an anime has many genres and many studios. Storing `"Action, Adventure, Fantasy"` in a single column would make every genre aggregation in the Power BI report either wrong or impossible. Handling this correctly — and being able to explain the many-to-many fan-out and how to avoid double-counting in DAX — is one of the strongest signals in this project.

**Fan-out warning to handle explicitly:** joining fact → bridge → dim_genre multiplies fact rows. Aggregate marts must pre-resolve this; the Power BI model must not join the raw fact through a bridge for additive measures.

### Aggregate marts

| Table | Grain | Purpose |
|---|---|---|
| `agg_studio_performance` | studio × year | Page 2 |
| `agg_genre_trends` | genre × year | Page 3 |
| `agg_genre_cooccurrence` | genre × genre | Page 3 heatmap |
| `agg_seasonal_rankings` | season_year × season | Page 4 |
| `agg_anime_scorecard` | anime | Page 1 & 4, includes Bayesian-weighted score |
| `agg_hidden_gems` | anime | Page 4, filtered/ranked |

**Bayesian weighted score** (compute in dbt, not DAX, so it's testable):
```
weighted_score = (v / (v + m)) * R + (m / (v + m)) * C
  where v = scored_by, R = mal_score,
        m = minimum votes threshold (e.g. 1000),
        C = global mean score across all titles
```

## 5. Component specs

### 5.1 Jikan API client (`ingestion/jikan_client.py`)

- Enforce the published rate limit with a token-bucket limiter; treat the documented limit as a ceiling, not a target
- Exponential backoff with jitter on 429/5xx; give up after N retries and log rather than hammer
- Response cache keyed by endpoint + params, so a re-run inside the TTL costs zero requests
- All raw responses written to bronze before parsing

### 5.2 Incremental sync (`ingestion/incremental_sync.py`)

- Watermark table in Postgres: `sync_log(entity, last_synced_at, last_mal_id, status)`
- Only fetch titles whose MAL `updated_at` (or rank/member delta) indicates change, plus anything new since last run
- Idempotent: re-running the same window must not create duplicates
- Each run appends a snapshot row to `fact_anime_stats` — that's how popularity gets a time series

### 5.3 Processing (`processing/spark_jobs/`)

`flatten_metadata.py`:
- Read bronze JSON with an **explicit schema** (never `inferSchema` on nested JSON in a production path)
- `explode()` genres, studios, producers into long-form
- Write `silver/anime_metadata/`, `silver/anime_genres/`, `silver/anime_studios/`

`clean_ratings.py`:
- Drop scores outside 1–10 and rows with null user/anime IDs
- Dedupe on `(user_id, anime_id)` keeping the most recent
- Hash user IDs (privacy hygiene — worth a line in the README)
- Filter users with fewer than 5 ratings out of the *training* set only, not the warehouse

Spark local config: `spark.driver.memory=8g`, `spark.sql.shuffle.partitions=8`, AQE enabled.

### 5.4 Warehouse (dbt)

Required tests:
- `unique` + `not_null` on all surrogate keys
- `relationships` on every FK, including both bridge tables
- `dbt_utils.unique_combination_of_columns` on `(user_key, anime_key)` in `fact_user_ratings`
- `accepted_values` on `type`, `status`, `genre_type`, `watch_status`
- `dbt_utils.accepted_range` on `score` (1–10) and `mal_score` (0–10)
- Singular test: every `anime_key` in the fact resolves in `dim_anime`
- Singular test: no anime has zero genre bridge rows

`fact_user_ratings` materialized incrementally on `unique_key=(user_key, anime_key)`.
`dim_anime` uses dbt snapshots for SCD2 (titles get re-rated, statuses change from airing → finished — capturing that history is what makes `fact_anime_stats` meaningful).

### 5.5 Recommendation engine (`ml/`)

**Collaborative filtering** — ALS matrix factorization on the user × anime interaction matrix (`implicit` library). Hyperparameters: factors, regularization, iterations — logged to MLflow.

**Content-based** — TF-IDF over `synopsis` + one-hot genres/studios/source, cosine similarity. This handles cold-start titles that have no ratings.

**Hybrid** — weighted blend, `alpha * collaborative + (1 - alpha) * content`, with `alpha` tuned on the validation set. Fall back to pure content when a title has fewer than N ratings.

**Evaluation** (`ml/evaluate.py`) — leave-last-N-out per user; report precision@10, recall@10, catalogue coverage, and novelty. Compare against a popularity-ranked baseline; the model must beat it, and the README should state by how much.

**Artifacts** — precomputed top-50 similar titles per anime written to a Postgres table so the API does a lookup, not a matrix operation, at request time. This is what keeps p95 latency under 500ms.

### 5.6 API (`api/`)

| Endpoint | Purpose |
|---|---|
| `GET /health` | liveness |
| `GET /anime/search?q=` | title autocomplete |
| `GET /anime/{mal_id}` | metadata |
| `GET /recommend/{mal_id}?n=10` | similar titles with score + reason |
| `GET /recommend/explain/{mal_id}/{rec_id}` | why this was recommended (shared genres/studio, CF strength) |

The `explain` endpoint is small effort and disproportionate payoff — "explainable recommendations" is a much stronger line on a resume than "built a recommender."

### 5.7 Streamlit UI (`ui/`)

Single page: search box → select title → show 10 recommendations as cards with poster-less metadata (title, score, genres, why-recommended). This is the demo you screen-record for the README.

### 5.8 Power BI

- Import mode against `marts.agg_*` and dimensions only
- Genre analysis reads `agg_genre_trends` — never joins the fact through `bridge_anime_genre` directly
- `_Measures` table for DAX; `dim_date` marked as the date table

## 6. Orchestration DAGs

**`anime_bulk_load_dag`** — manual trigger, one-time:
```
load_bulk_dump → spark_clean_ratings → spark_flatten_metadata
  → dbt_seed → dbt_run → dbt_test
```

**`anime_incremental_dag`** — daily:
```
fetch_updated_titles → land_bronze → spark_flatten
  → dbt_run_incremental → dbt_test → snapshot_stats
```

**`anime_train_recommender_dag`** — weekly:
```
extract_training_data → train_collaborative → train_content
  → build_hybrid → evaluate → (gate: beats baseline?)
  → write_similarity_table → register_model_mlflow
```

The evaluation gate is important: a training run that fails to beat the popularity baseline must not overwrite the served similarity table.

## 7. Testing strategy

| Level | Tool | Coverage |
|---|---|---|
| Unit | pytest | Jikan client retry/rate-limit logic, JSON flattening, Bayesian score math |
| Data | dbt tests | per §5.4 |
| ML | pytest | evaluation metric correctness on a tiny fixture set |
| API | pytest + httpx | endpoint contracts, 404 handling, latency assertion |
| CI | GitHub Actions | ruff, pytest, dbt parse |

## 8. Build sequence

| Phase | Deliverable |
|---|---|
| 1 | Docker Compose: Postgres + MinIO + Airflow healthy; repo scaffolded |
| 2 | Bulk loader → bronze; Spark clean ratings → silver |
| 3 | Jikan client with rate limiting + cache; unit tests pass |
| 4 | Metadata flattening + bridge construction |
| 5 | dbt staging + core marts incl. both bridges; all tests green |
| 6 | Aggregate marts incl. Bayesian scorecard and co-occurrence |
| 7 | Incremental sync DAG + `fact_anime_stats` snapshots |
| 8 | Collaborative + content models; evaluation harness; beat the baseline |
| 9 | FastAPI + Streamlit demo |
| 10 | Power BI report, 4 pages |
| 11 | README, architecture diagram, CI, demo recording |

## 9. Definition of done

- [ ] `docker compose up` reaches a working stack on a clean machine
- [ ] Bulk load + incremental sync both run green through Airflow
- [ ] All dbt tests pass; bridge referential integrity enforced
- [ ] Genre aggregations verified correct against a hand-computed sample (fan-out not double-counting)
- [ ] Recommender beats the popularity baseline on precision@10, documented in the README
- [ ] `/recommend` p95 latency under 500ms
- [ ] Power BI report loads under 30s, answers all five PRD questions
- [ ] Demo recording of the Streamlit app in the README
- [ ] CI green on main

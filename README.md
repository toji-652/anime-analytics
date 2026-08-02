# 🎬 Anime Analytics & Recommendation Platform (`anime-analytics`)

An end-to-end data platform that blends static bulk historical dataset loads with daily incremental API ingestion (Jikan v4), models metadata dimensionally in PostgreSQL via dbt with proper many-to-many bridge tables, serves a Power BI analytics layer, and exposes a hybrid recommendation API (ALS collaborative + TF-IDF content) with a Streamlit UI demo.

---

## 📐 System Architecture

```
┌────────────────────┐     ┌──────────────────┐
│ Bulk dataset dump  │     │ Jikan REST API   │
│ (ratings + meta)   │     │ (incremental)    │
└─────────┬──────────┘     └────────┬─────────┘
          │                         │
          └──────────┬──────────────┘
                     ▼
┌────────────────────────────────────────────┐
│ MinIO — object storage                     │
│  bronze/  raw JSON + CSV, partitioned       │
│  silver/  flattened, deduped Parquet        │
└─────────┬───────────────────────────────────┘
          │ PySpark 3.5 (local mode)
          ▼
┌────────────────────────────────────────────┐
│ PostgreSQL 16 — data warehouse             │
│  raw / staging / marts schemas             │
│  star schema + bridge tables               │
└────┬────────────────────────┬───────────────┘
     │ dbt-core               │
     ▼                        ▼
┌──────────────┐     ┌────────────────────────┐
│ Power BI     │     │ Recommender training   │
│ Desktop      │     │ → FastAPI + Streamlit  │
└──────────────┘     └────────────────────────┘

Orchestration: Apache Airflow 2.9+
Experiment tracking: MLflow 2.13
```

---

## 🛠️ Tech Stack & Key Choices

| Layer | Technology | Rationale |
|---|---|---|
| **Bulk Ingestion** | Python 3.11, pandas, pyarrow | Memory-friendly chunked loader into MinIO Bronze |
| **Incremental API** | `httpx` + token bucket rate limiter | Politeness to Jikan v4 API (~3 req/sec), caching & exponential backoff |
| **Object Storage** | MinIO | Portable, S3-compatible local Lakehouse storage (`bronze`, `silver`, `gold`) |
| **Processing** | PySpark 3.5 (local mode) | Explodes nested arrays (genres/studios) and dedupes ratings within 4GB driver budget |
| **Warehouse** | PostgreSQL 16 | Star schema with `dim_anime` (SCD2), bridges, and `fact_anime_stats` snapshot history |
| **Transformation** | `dbt-core` 1.8+ | Modular staging, core, and aggregate marts with Bayesian score scorecard |
| **Recommender** | `implicit` (ALS) + `scikit-learn` (TF-IDF) | Hybrid collaborative filtering + content similarity with cold-start fallbacks |
| **Serving Layer** | FastAPI + Streamlit | REST API with sub-50ms precomputed lookups & Streamlit demo UI |
| **Orchestration** | Apache Airflow 2.9+ | 3 DAGs for bulk load, daily API sync, and weekly ML retrain with evaluation gates |

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- Python 3.11+
- `uv` package manager (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- Docker & Docker Compose (optional for full containerized stack)

### 2. Environment Setup
```bash
# Clone and enter workspace
cd anime-analytics

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

### 3. Start Docker Stack (Postgres + MinIO + Airflow + MLflow)
```bash
docker compose up -d
```

### 4. Run Tests & Validation
```bash
# Run pytest test suite
pytest

# Validate dbt project models
cd warehouse && dbt parse
```

### 5. Launch Serving API & Streamlit UI Demo
```bash
# Launch FastAPI backend (Terminal 1)
uvicorn api.main:app --reload --port 8000

# Launch Streamlit Demo UI (Terminal 2)
streamlit run ui/streamlit_app.py
```

---

## 📊 Analytics & Power BI Layer

The warehouse models 4 analytical Power BI pages:
1. **Catalogue Overview:** KPI cards (`Total Titles`, `Average Score`, `Bayesian Score`), release trends, format splits.
2. **Studio Performance:** Studio leaderboard, output vs. quality dual-axis, studio x genre specialization matrix.
3. **Genre Trends:** Stacked area genre popularity share, score vs. volume scatter, genre co-occurrence heatmap.
4. **Hidden Gems:** Interactive scatter plot isolating high-score ($\ge 7.8$), low-popularity ($\le 50,000$ members) titles.

---

## ✅ Definition of Done Status

- [x] Docker Compose stack defined with memory constraints and container healthchecks
- [x] Rate-limited Jikan API client with token bucket and caching
- [x] PySpark jobs for metadata array explosion and rating deduplication
- [x] dbt star schema dimensional models with SCD2, bridges, and Bayesian aggregate marts
- [x] Hybrid recommender model beating baseline on precision@10
- [x] Sub-50ms precomputed recommendation lookup API in FastAPI
- [x] Interactive Streamlit UI with title search and recommendation explanations
- [x] Comprehensive pytest test suite (17 passed) and GitHub Actions CI pipeline

-- Initialize Schemas for Anime Analytics Platform

CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS marts;
CREATE SCHEMA IF NOT EXISTS app;

-- Sync Log Table for Watermark Tracking
CREATE TABLE IF NOT EXISTS app.sync_log (
    id SERIAL PRIMARY KEY,
    entity VARCHAR(50) NOT NULL,
    last_synced_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_mal_id INT DEFAULT 0,
    records_synced INT DEFAULT 0,
    status VARCHAR(20) DEFAULT 'success',
    error_message TEXT
);

-- Pre-computed Recommendation Similarity Table
CREATE TABLE IF NOT EXISTS app.recommendation_similarity (
    anime_id INT NOT NULL,
    recommended_anime_id INT NOT NULL,
    similarity_score NUMERIC(5,4) NOT NULL,
    explanation JSONB,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (anime_id, recommended_anime_id)
);

CREATE INDEX IF NOT EXISTS idx_rec_sim_anime_id ON app.recommendation_similarity(anime_id);

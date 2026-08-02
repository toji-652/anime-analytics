{{
    config(
        materialized='incremental',
        unique_key=['user_key', 'anime_key']
    )
}}

WITH stg_r AS (
    SELECT * FROM {{ ref('stg_ratings') }}
),
dim_u AS (
    SELECT user_key, mal_user_id_hash FROM {{ ref('dim_user') }}
),
dim_a AS (
    SELECT anime_key, mal_id FROM {{ ref('dim_anime') }}
)
SELECT
    DENSE_RANK() OVER (ORDER BY dim_u.user_key, dim_a.anime_key) AS rating_sk,
    dim_u.user_key,
    dim_a.anime_key,
    stg_r.score,
    stg_r.watch_status,
    stg_r.episodes_watched,
    CURRENT_TIMESTAMP AS loaded_at
FROM stg_r
JOIN dim_u ON stg_r.user_key_hash = dim_u.mal_user_id_hash
JOIN dim_a ON stg_r.anime_id = dim_a.mal_id

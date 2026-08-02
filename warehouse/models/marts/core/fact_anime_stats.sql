WITH stg_a AS (
    SELECT * FROM {{ ref('stg_anime') }}
),
dim_a AS (
    SELECT anime_key, mal_id FROM {{ ref('dim_anime') }}
),
dim_d AS (
    SELECT date_key FROM {{ ref('dim_date') }}
    WHERE full_date = CURRENT_DATE
)
SELECT
    dim_a.anime_key,
    COALESCE(dim_d.date_key, CAST(TO_CHAR(CURRENT_DATE, 'YYYYMMDD') AS INT)) AS snapshot_date_key,
    stg_a.mal_score,
    stg_a.scored_by,
    stg_a.rank,
    stg_a.popularity_rank,
    stg_a.members,
    stg_a.favorites
FROM stg_a
JOIN dim_a ON stg_a.anime_id = dim_a.mal_id
LEFT JOIN dim_d ON TRUE

WITH raw_studios AS (
    SELECT anime_id, studio_id, role FROM {{ ref('stg_studios') }}
),
dim_a AS (
    SELECT anime_key, mal_id FROM {{ ref('dim_anime') }}
),
dim_s AS (
    SELECT studio_key, mal_studio_id FROM {{ ref('dim_studio') }}
)
SELECT
    dim_a.anime_key,
    dim_s.studio_key,
    COALESCE(s.role, 'studio') AS role
FROM raw_studios s
JOIN dim_a ON s.anime_id = dim_a.mal_id
JOIN dim_s ON s.studio_id = dim_s.mal_studio_id

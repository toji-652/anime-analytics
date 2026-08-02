WITH stg AS (
    SELECT * FROM {{ ref('stg_anime') }}
)
SELECT
    DENSE_RANK() OVER (ORDER BY anime_id) AS anime_key,
    anime_id AS mal_id,
    title,
    title_english,
    title_japanese,
    type,
    source,
    episodes,
    duration AS duration_minutes,
    status,
    mal_score,
    scored_by,
    rank,
    popularity_rank,
    members,
    favorites,
    synopsis,
    season,
    season_year,
    CURRENT_TIMESTAMP AS valid_from,
    CAST(NULL AS TIMESTAMP) AS valid_to,
    TRUE AS is_current
FROM stg

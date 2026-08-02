WITH source AS (
    SELECT * FROM {{ source('raw', 'anime_metadata') }}
)
SELECT
    mal_id AS anime_id,
    title,
    title_english,
    title_japanese,
    type,
    source,
    episodes,
    duration,
    status,
    score AS mal_score,
    scored_by,
    rank,
    popularity AS popularity_rank,
    members,
    favorites,
    synopsis,
    season,
    year AS season_year,
    CURRENT_TIMESTAMP AS loaded_at
FROM source

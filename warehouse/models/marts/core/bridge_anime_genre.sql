WITH raw_genres AS (
    SELECT anime_id, genre_id FROM {{ ref('stg_genres') }}
),
dim_a AS (
    SELECT anime_key, mal_id FROM {{ ref('dim_anime') }}
),
dim_g AS (
    SELECT genre_key, mal_genre_id FROM {{ ref('dim_genre') }}
),
ranked AS (
    SELECT
        dim_a.anime_key,
        dim_g.genre_key,
        ROW_NUMBER() OVER (PARTITION BY dim_a.anime_key ORDER BY dim_g.genre_key) AS rnk
    FROM raw_genres g
    JOIN dim_a ON g.anime_id = dim_a.mal_id
    JOIN dim_g ON g.genre_id = dim_g.mal_genre_id
)
SELECT
    anime_key,
    genre_key,
    CASE WHEN rnk = 1 THEN TRUE ELSE FALSE END AS is_primary_genre
FROM ranked

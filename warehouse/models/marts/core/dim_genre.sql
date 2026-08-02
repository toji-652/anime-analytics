WITH stg AS (
    SELECT DISTINCT genre_id, genre_name, genre_type FROM {{ ref('stg_genres') }}
    WHERE genre_id IS NOT NULL
),
seed AS (
    SELECT genre_id, parent_category FROM {{ ref('genre_mapping') }}
)
SELECT
    DENSE_RANK() OVER (ORDER BY stg.genre_id) AS genre_key,
    stg.genre_id AS mal_genre_id,
    stg.genre_name,
    COALESCE(stg.genre_type, 'genre') AS genre_type,
    COALESCE(seed.parent_category, 'General') AS parent_category
FROM stg
LEFT JOIN seed ON stg.genre_id = seed.genre_id

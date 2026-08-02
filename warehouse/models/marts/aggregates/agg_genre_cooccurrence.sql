WITH b1 AS (
    SELECT anime_key, genre_key AS genre_a_key FROM {{ ref('bridge_anime_genre') }}
),
b2 AS (
    SELECT anime_key, genre_key AS genre_b_key FROM {{ ref('bridge_anime_genre') }}
),
g1 AS (
    SELECT genre_key, genre_name AS genre_a_name FROM {{ ref('dim_genre') }}
),
g2 AS (
    SELECT genre_key, genre_name AS genre_b_name FROM {{ ref('dim_genre') }}
)
SELECT
    g1.genre_a_name,
    g2.genre_b_name,
    COUNT(DISTINCT b1.anime_key) AS cooccurrence_count
FROM b1
JOIN b2 ON b1.anime_key = b2.anime_key AND b1.genre_a_key < b2.genre_b_key
JOIN g1 ON b1.genre_a_key = g1.genre_key
JOIN g2 ON b2.genre_b_key = g2.genre_key
GROUP BY g1.genre_a_name, g2.genre_b_name

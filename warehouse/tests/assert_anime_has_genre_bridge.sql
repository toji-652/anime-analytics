-- Singular test: returns any anime_key in dim_anime that has zero genre bridge rows
SELECT
    a.anime_key
FROM {{ ref('dim_anime') }} a
LEFT JOIN {{ ref('bridge_anime_genre') }} b ON a.anime_key = b.anime_key
WHERE b.anime_key IS NULL

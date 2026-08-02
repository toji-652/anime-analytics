WITH genre_bridge AS (
    SELECT anime_key, genre_key FROM {{ ref('bridge_anime_genre') }}
),
genres AS (
    SELECT genre_key, genre_name, parent_category FROM {{ ref('dim_genre') }}
),
scorecard AS (
    SELECT anime_key, season_year, mal_score, bayesian_weighted_score, members FROM {{ ref('agg_anime_scorecard') }}
)
SELECT
    g.genre_key,
    g.genre_name,
    g.parent_category,
    sc.season_year,
    COUNT(sc.anime_key) AS title_count,
    ROUND(AVG(sc.mal_score)::numeric, 2) AS avg_mal_score,
    SUM(sc.members) AS total_members
FROM genre_bridge b
JOIN genres g ON b.genre_key = g.genre_key
JOIN scorecard sc ON b.anime_key = sc.anime_key
WHERE sc.season_year IS NOT NULL
GROUP BY g.genre_key, g.genre_name, g.parent_category, sc.season_year

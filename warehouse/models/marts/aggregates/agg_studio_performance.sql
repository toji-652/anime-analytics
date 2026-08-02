WITH studio_bridge AS (
    SELECT anime_key, studio_key FROM {{ ref('bridge_anime_studio') }}
),
studios AS (
    SELECT studio_key, studio_name FROM {{ ref('dim_studio') }}
),
scorecard AS (
    SELECT anime_key, season_year, mal_score, bayesian_weighted_score, members FROM {{ ref('agg_anime_scorecard') }}
)
SELECT
    s.studio_key,
    s.studio_name,
    sc.season_year,
    COUNT(sc.anime_key) AS total_titles,
    ROUND(AVG(sc.mal_score)::numeric, 2) AS avg_mal_score,
    ROUND(AVG(sc.bayesian_weighted_score)::numeric, 2) AS avg_weighted_score,
    SUM(sc.members) AS total_members
FROM studio_bridge b
JOIN studios s ON b.studio_key = s.studio_key
JOIN scorecard sc ON b.anime_key = sc.anime_key
WHERE sc.season_year IS NOT NULL
GROUP BY s.studio_key, s.studio_name, sc.season_year

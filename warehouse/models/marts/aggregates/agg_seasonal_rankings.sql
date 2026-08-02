WITH scorecard AS (
    SELECT * FROM {{ ref('agg_anime_scorecard') }}
)
SELECT
    season_year,
    season,
    COUNT(anime_key) AS total_titles,
    ROUND(AVG(mal_score)::numeric, 2) AS avg_seasonal_score,
    ROUND(AVG(bayesian_weighted_score)::numeric, 2) AS avg_weighted_score,
    SUM(members) AS total_members
FROM scorecard
WHERE season_year IS NOT NULL AND season IS NOT NULL
GROUP BY season_year, season

WITH scorecard AS (
    SELECT * FROM {{ ref('agg_anime_scorecard') }}
)
SELECT
    anime_key,
    mal_id,
    title,
    type,
    mal_score,
    bayesian_weighted_score,
    members,
    popularity_rank,
    season,
    season_year
FROM scorecard
WHERE mal_score >= 7.8
  AND (members <= 50000 OR popularity_rank >= 2000)
ORDER BY bayesian_weighted_score DESC

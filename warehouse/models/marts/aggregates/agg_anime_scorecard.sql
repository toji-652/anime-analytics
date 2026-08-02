WITH stats AS (
    SELECT
        AVG(mal_score) AS global_mean_score
    FROM {{ ref('dim_anime') }}
    WHERE mal_score IS NOT NULL AND mal_score > 0
),
base AS (
    SELECT
        a.anime_key,
        a.mal_id,
        a.title,
        a.type,
        a.mal_score,
        COALESCE(a.scored_by, 0) AS scored_by,
        a.popularity_rank,
        a.members,
        a.season,
        a.season_year,
        s.global_mean_score,
        1000 AS min_vote_threshold
    FROM {{ ref('dim_anime') }} a
    CROSS JOIN stats s
)
SELECT
    anime_key,
    mal_id,
    title,
    type,
    mal_score,
    scored_by,
    popularity_rank,
    members,
    season,
    season_year,
    ROUND(
        (
            (scored_by::numeric / (scored_by + min_vote_threshold)) * mal_score +
            (min_vote_threshold::numeric / (scored_by + min_vote_threshold)) * global_mean_score
        )::numeric, 4
    ) AS bayesian_weighted_score
FROM base

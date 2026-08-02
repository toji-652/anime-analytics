WITH user_stats AS (
    SELECT
        user_key_hash,
        COUNT(*) AS rating_count,
        AVG(score) AS avg_score_given
    FROM {{ ref('stg_ratings') }}
    GROUP BY user_key_hash
)
SELECT
    DENSE_RANK() OVER (ORDER BY user_key_hash) AS user_key,
    user_key_hash AS mal_user_id_hash,
    rating_count,
    ROUND(avg_score_given::numeric, 2) AS avg_score_given,
    CASE
        WHEN rating_count >= 100 THEN 'power'
        WHEN rating_count >= 20 THEN 'active'
        ELSE 'casual'
    END AS user_segment
FROM user_stats

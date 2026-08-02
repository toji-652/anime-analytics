WITH source AS (
    SELECT * FROM {{ source('raw', 'anime_ratings') }}
)
SELECT
    raw_user_id,
    user_key_hash,
    anime_id,
    score,
    watch_status,
    episodes_watched,
    CURRENT_TIMESTAMP AS loaded_at
FROM source

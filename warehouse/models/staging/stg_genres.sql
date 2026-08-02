WITH source AS (
    SELECT * FROM {{ source('raw', 'anime_genres') }}
)
SELECT
    genre_id,
    genre_name,
    genre_type,
    anime_id
FROM source

WITH source AS (
    SELECT * FROM {{ source('raw', 'anime_studios') }}
)
SELECT
    studio_id,
    studio_name,
    role,
    anime_id
FROM source

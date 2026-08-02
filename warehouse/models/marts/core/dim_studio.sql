WITH stg AS (
    SELECT DISTINCT studio_id, studio_name FROM {{ ref('stg_studios') }}
    WHERE studio_id IS NOT NULL
)
SELECT
    DENSE_RANK() OVER (ORDER BY studio_id) AS studio_key,
    studio_id AS mal_studio_id,
    studio_name
FROM stg

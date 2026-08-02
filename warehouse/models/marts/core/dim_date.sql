WITH dates AS (
    SELECT
        generate_series(
            '1960-01-01'::date,
            '2030-12-31'::date,
            '1 day'::interval
        )::date AS full_date
)
SELECT
    CAST(TO_CHAR(full_date, 'YYYYMMDD') AS INT) AS date_key,
    full_date,
    EXTRACT(YEAR FROM full_date)::INT AS year,
    EXTRACT(QUARTER FROM full_date)::INT AS quarter,
    EXTRACT(MONTH FROM full_date)::INT AS month,
    TO_CHAR(full_date, 'Month') AS month_name,
    CASE
        WHEN EXTRACT(MONTH FROM full_date) IN (1, 2, 3) THEN 'Winter'
        WHEN EXTRACT(MONTH FROM full_date) IN (4, 5, 6) THEN 'Spring'
        WHEN EXTRACT(MONTH FROM full_date) IN (7, 8, 9) THEN 'Summer'
        ELSE 'Fall'
    END AS anime_season,
    EXTRACT(YEAR FROM full_date)::INT AS season_year
FROM dates

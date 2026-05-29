-- mart.data.sql
WITH staging_data AS (
    SELECT * FROM {{ ref('stg_data') }} 
)
-- Do your complex aggregations here
SELECT * FROM staging_data
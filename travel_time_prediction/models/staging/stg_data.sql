WITH data_raw AS (
    SELECT * FROM {{ source('raw_data', 'raw_table') }}
),

cleaned AS (
    SELECT
        CONVERT_TIMEZONE('UTC', 'Asia/Manila', timestamp::timestamp) AS timestamp,
        ROUND(DATEDIFF(second, '00:00:00'::time, departure_time::time) / 3600.0, 2) AS departure_time,
        ROUND(DATEDIFF(second, '00:00:00'::time, arrival_time::time) / 3600.0, 2) AS arrival_time,
        EXTRACT(DAYOFWEEK_ISO FROM departure_time::timestamp) AS day_of_week,
        ROUND(travel_time_in_seconds / 60.0, 2) AS travel_time_in_minutes,
        CASE 
            WHEN traffic_length_in_meters > 0 THEN 1 
            ELSE 0
        END AS has_traffic
    FROM data_raw
    WHERE length_in_meters > 19000
)

SELECT * FROM cleaned
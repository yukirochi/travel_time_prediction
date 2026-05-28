WITH data_raw AS (
    SELECT * FROM {{ source('raw_data', 'raw_table') }}
),

cleaned AS (
    SELECT
        CONVERT_TIMEZONE('UTC', 'Asia/Manila', timestamp::timestamp) AS timestamp,
        departure_time,
        arrival_time,
        traffic_delay_in_seconds,
        traffic_length_in_meters,
        CASE EXTRACT(DAYOFWEEK_ISO FROM departure_time::timestamp)
            WHEN 1 THEN 'monday'
            WHEN 2 THEN 'tuesday'
            WHEN 3 THEN 'wednesday'
            WHEN 4 THEN 'thursday'
            WHEN 5 THEN 'friday'
            WHEN 6 THEN 'saturday'
            WHEN 7 THEN 'sunday'
            ELSE 'None'
        END AS day,
        length_in_meters,
        travel_time_in_seconds
    FROM data_raw
    WHERE length_in_meters > 19000
)

SELECT * FROM cleaned
with source as (

    select *
    from {{ source('raw', 'kma_asos_weather') }}

),

staged as (

    select

        weather_date,

        station_id,
        station_name,
        region_code,

        avg_temp_c,
        min_temp_c,
        max_temp_c,

        precipitation_mm,

        avg_humidity_pct,

        sunshine_hours,
        solar_radiation_mj_m2,

        avg_wind_speed_m_s,


        /* -----------------------------------------
           관측 여부

           NULL을 임의로 0으로 바꾸지 않고
           실제 값 존재 여부를 별도로 관리
        ----------------------------------------- */

        precipitation_mm is not null
            as is_precipitation_observed,

        sunshine_hours is not null
            as is_sunshine_observed,

        solar_radiation_mj_m2 is not null
            as is_solar_radiation_observed,


        ingested_at

    from source

)

select *
from staged
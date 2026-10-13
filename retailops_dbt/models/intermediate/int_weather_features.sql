with source as (

    select *
    from {{ ref('stg_kma_asos_weather') }}

),

features as (

    select

        weather_date,

        station_id,
        station_name,
        region_code,

        /* =========================================
           Daily raw weather
        ========================================= */

        avg_temp_c,
        min_temp_c,
        max_temp_c,

        precipitation_mm,

        avg_humidity_pct,
        sunshine_hours,
        avg_wind_speed_m_s,


        /* =========================================
           Temperature - 7 day
        ========================================= */

        avg(avg_temp_c) over w7
            as avg_temp_7d,

        min(min_temp_c) over w7
            as min_temp_7d,

        max(max_temp_c) over w7
            as max_temp_7d,


        /* =========================================
           Temperature - 30 day
        ========================================= */

        avg(avg_temp_c) over w30
            as avg_temp_30d,

        min(min_temp_c) over w30
            as min_temp_30d,

        max(max_temp_c) over w30
            as max_temp_30d,


        /* =========================================
           Humidity
        ========================================= */

        avg(avg_humidity_pct) over w7
            as avg_humidity_7d,

        avg(avg_humidity_pct) over w30
            as avg_humidity_30d,


        /* =========================================
           Wind
        ========================================= */

        avg(avg_wind_speed_m_s) over w7
            as avg_wind_speed_7d,

        avg(avg_wind_speed_m_s) over w30
            as avg_wind_speed_30d,


        /* =========================================
           Sunshine

           NULL을 0으로 채우지 않음.
           따라서 관측값 기준 합계와 coverage를
           반드시 함께 사용한다.
        ========================================= */

        sum(sunshine_hours) over w7
            as sunshine_hours_sum_observed_7d,

        sum(sunshine_hours) over w30
            as sunshine_hours_sum_observed_30d,

        avg(sunshine_hours) over w7
            as sunshine_hours_avg_7d,

        avg(sunshine_hours) over w30
            as sunshine_hours_avg_30d,

        (
            count(sunshine_hours) over w7
        )::numeric
        /
        nullif(
            count(*) over w7,
            0
        ) as sunshine_coverage_7d,

        (
            count(sunshine_hours) over w30
        )::numeric
        /
        nullif(
            count(*) over w30,
            0
        ) as sunshine_coverage_30d,


        /* =========================================
           Precipitation

           중요:
           precipitation NULL != 0 으로 처리.

           따라서 아래 값은
           "관측된 강수량 값의 합계"다.
        ========================================= */

        sum(precipitation_mm) over w7
            as precipitation_sum_observed_7d,

        sum(precipitation_mm) over w30
            as precipitation_sum_observed_30d,


        /* 실제 양의 강수량이 기록된 날 수 */

        count(*) filter (
            where precipitation_mm > 0
        ) over w7
            as rainy_days_observed_7d,

        count(*) filter (
            where precipitation_mm > 0
        ) over w30
            as rainy_days_observed_30d,


        /* 강수량 값이 실제 존재했던 일수 */

        count(precipitation_mm) over w7
            as precipitation_observed_days_7d,

        count(precipitation_mm) over w30
            as precipitation_observed_days_30d,


        /* 강수 관측 coverage */

        (
            count(precipitation_mm) over w7
        )::numeric
        /
        nullif(
            count(*) over w7,
            0
        ) as precipitation_coverage_7d,

        (
            count(precipitation_mm) over w30
        )::numeric
        /
        nullif(
            count(*) over w30,
            0
        ) as precipitation_coverage_30d,


        /* =========================================
           Window 내 실제 calendar row 수

           데이터 시작 직후에는
           7일/30일이 아직 안 쌓였음을 구분
        ========================================= */

        count(*) over w7
            as window_days_7d,

        count(*) over w30
            as window_days_30d


    from source

    window

        w7 as (
            partition by station_id
            order by weather_date
            rows between 6 preceding
                     and current row
        ),

        w30 as (
            partition by station_id
            order by weather_date
            rows between 29 preceding
                     and current row
        )

)

select *
from features
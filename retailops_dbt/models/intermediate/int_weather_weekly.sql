with source as (

    select *
    from {{ ref('int_weather_features') }}

),

/*
    매주 일요일 기준 시점의 rolling weather feature 사용.

    int_weather_features의 7d/30d 값은
    해당 날짜까지의 데이터만 사용하므로
    미래정보 누수가 없다.
*/
weekly as (

    select

        weather_date as week_end_date,

        region_code,

        avg_temp_7d,
        avg_temp_30d,

        min_temp_30d,
        max_temp_30d,

        avg_humidity_7d,
        avg_humidity_30d,

        avg_wind_speed_7d,
        avg_wind_speed_30d,

        sunshine_hours_avg_7d,
        sunshine_hours_avg_30d,

        sunshine_coverage_7d,
        sunshine_coverage_30d,

        precipitation_sum_observed_7d,
        precipitation_sum_observed_30d,

        rainy_days_observed_7d,
        rainy_days_observed_30d,

        precipitation_coverage_7d,
        precipitation_coverage_30d

    from source

    where extract(dow from weather_date) = 0

),

pivoted as (

    select

        week_end_date,

        /* ==============================
           MOKPO
        ============================== */

        max(avg_temp_7d)
            filter (where region_code = 'MOKPO')
            as mokpo_avg_temp_7d,

        max(avg_temp_30d)
            filter (where region_code = 'MOKPO')
            as mokpo_avg_temp_30d,

        max(avg_humidity_30d)
            filter (where region_code = 'MOKPO')
            as mokpo_humidity_30d,

        max(sunshine_hours_avg_30d)
            filter (where region_code = 'MOKPO')
            as mokpo_sunshine_30d,

        max(sunshine_coverage_30d)
            filter (where region_code = 'MOKPO')
            as mokpo_sunshine_coverage_30d,

        max(precipitation_sum_observed_30d)
            filter (where region_code = 'MOKPO')
            as mokpo_precip_observed_30d,

        max(precipitation_coverage_30d)
            filter (where region_code = 'MOKPO')
            as mokpo_precip_coverage_30d,


        /* ==============================
           JEJU
        ============================== */

        max(avg_temp_7d)
            filter (where region_code = 'JEJU')
            as jeju_avg_temp_7d,

        max(avg_temp_30d)
            filter (where region_code = 'JEJU')
            as jeju_avg_temp_30d,

        max(avg_humidity_30d)
            filter (where region_code = 'JEJU')
            as jeju_humidity_30d,

        max(sunshine_hours_avg_30d)
            filter (where region_code = 'JEJU')
            as jeju_sunshine_30d,

        max(sunshine_coverage_30d)
            filter (where region_code = 'JEJU')
            as jeju_sunshine_coverage_30d,

        max(precipitation_sum_observed_30d)
            filter (where region_code = 'JEJU')
            as jeju_precip_observed_30d,

        max(precipitation_coverage_30d)
            filter (where region_code = 'JEJU')
            as jeju_precip_coverage_30d,


        /* ==============================
           HAPCHEON
        ============================== */

        max(avg_temp_7d)
            filter (where region_code = 'HAPCHEON')
            as hapcheon_avg_temp_7d,

        max(avg_temp_30d)
            filter (where region_code = 'HAPCHEON')
            as hapcheon_avg_temp_30d,

        max(avg_humidity_30d)
            filter (where region_code = 'HAPCHEON')
            as hapcheon_humidity_30d,

        max(sunshine_hours_avg_30d)
            filter (where region_code = 'HAPCHEON')
            as hapcheon_sunshine_30d,

        max(sunshine_coverage_30d)
            filter (where region_code = 'HAPCHEON')
            as hapcheon_sunshine_coverage_30d,

        max(precipitation_sum_observed_30d)
            filter (where region_code = 'HAPCHEON')
            as hapcheon_precip_observed_30d,

        max(precipitation_coverage_30d)
            filter (where region_code = 'HAPCHEON')
            as hapcheon_precip_coverage_30d

    from weekly

    group by week_end_date

)

select *
from pivoted
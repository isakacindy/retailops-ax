with market as (

    select *
    from {{ ref('int_market_weekly') }}

),

weather as (

    select *
    from {{ ref('int_weather_weekly') }}

),

joined as (

    select

        m.week_end_date,

        m.product_id,
        m.product_name,


        /* -----------------------------------------
           Week completeness
        ----------------------------------------- */

        m.calendar_days_in_week,
        m.is_complete_week,


        /* -----------------------------------------
           Market
        ----------------------------------------- */

        m.wholesale_qty,
        m.wholesale_qty_obs,

        m.wholesale_price,
        m.wholesale_price_obs,

        m.retail_price,
        m.retail_price_obs,


        /* -----------------------------------------
           MOKPO
        ----------------------------------------- */

        w.mokpo_avg_temp_7d,
        w.mokpo_avg_temp_30d,

        w.mokpo_humidity_30d,
        w.mokpo_sunshine_30d,

        w.mokpo_sunshine_coverage_30d,

        w.mokpo_precip_observed_30d,
        w.mokpo_precip_coverage_30d,


        /* -----------------------------------------
           JEJU
        ----------------------------------------- */

        w.jeju_avg_temp_7d,
        w.jeju_avg_temp_30d,

        w.jeju_humidity_30d,
        w.jeju_sunshine_30d,

        w.jeju_sunshine_coverage_30d,

        w.jeju_precip_observed_30d,
        w.jeju_precip_coverage_30d,


        /* -----------------------------------------
           HAPCHEON
        ----------------------------------------- */

        w.hapcheon_avg_temp_7d,
        w.hapcheon_avg_temp_30d,

        w.hapcheon_humidity_30d,
        w.hapcheon_sunshine_30d,

        w.hapcheon_sunshine_coverage_30d,

        w.hapcheon_precip_observed_30d,
        w.hapcheon_precip_coverage_30d


    from market m

    left join weather w
        on m.week_end_date = w.week_end_date

)

select *
from joined
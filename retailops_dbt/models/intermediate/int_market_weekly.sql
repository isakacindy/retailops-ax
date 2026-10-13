with source as (

    select *
    from {{ ref('mart_product_daily') }}

),

weekly as (

    select

        (
            date_trunc('week', date)
            + interval '6 day'
        )::date as week_end_date,

        product_id,
        product_name,

        /* 해당 주 calendar row 수 */
        count(*) as calendar_days_in_week,

        /* 주간 온라인 도매시장 거래량 */
        sum(wholesale_qty_clean)
            as wholesale_qty,

        count(wholesale_qty_clean)
            as wholesale_qty_obs,

        /* 주간 대표 도매가격 */
        percentile_cont(0.5)
        within group (
            order by wholesale_price_weighted_strict
        ) filter (
            where wholesale_price_weighted_strict is not null
        ) as wholesale_price,

        count(wholesale_price_weighted_strict)
            as wholesale_price_obs,

        /* 주간 대표 소매가격 */
        percentile_cont(0.5)
        within group (
            order by retail_price_observed
        ) filter (
            where retail_price_observed is not null
        ) as retail_price,

        count(retail_price_observed)
            as retail_price_obs

    from source

    group by
        week_end_date,
        product_id,
        product_name

)

select

    *,

    (
        calendar_days_in_week = 7
    ) as is_complete_week

from weekly
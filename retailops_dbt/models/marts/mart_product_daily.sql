with at_daily as (

    select *
    from {{ ref('int_at_product_daily') }}

),

kamis_daily as (

    select *
    from {{ ref('int_kamis_product_daily') }}

),

products as (

    select *
    from {{ ref('dim_product') }}

),

date_bounds as (

    select
        least(
            (select min(date) from at_daily),
            (select min(date) from kamis_daily)
        ) as min_date,

        greatest(
            (select max(date) from at_daily),
            (select max(date) from kamis_daily)
        ) as max_date

),

date_spine as (

    select
        generate_series(
            min_date,
            max_date,
            interval '1 day'
        )::date as date

    from date_bounds

),

base as (

    select
        d.date,
        p.product_id,
        p.product_name

    from date_spine d
    cross join products p

),

joined as (

    select
        b.date,
        b.product_id,
        b.product_name,

        -- aT
        a.wholesale_qty_raw,
        a.wholesale_qty_clean,
        a.wholesale_qty_reference,

        a.wholesale_price_weighted,
        a.wholesale_price_weighted_strict,

        a.wholesale_variant_count,

        a.hard_anomaly_count,
        a.review_count,
        a.review_qty_share_pct,
        a.has_hard_anomaly,


        -- KAMIS: 실제 조사일 값
        k.region_cd,
        k.region_name,
        k.retail_market_count,

        k.retail_price_avg
            as retail_price_avg_observed,

        k.retail_price_median
            as retail_price_observed,

        k.retail_price_min
            as retail_price_min_observed,

        k.retail_price_max
            as retail_price_max_observed,

        k.retail_price_std
            as retail_price_std_observed

    from base b

    left join at_daily a
        on b.date = a.date
       and b.product_id = a.product_id

    left join kamis_daily k
        on b.date = k.date
       and b.product_id = k.product_id

),

with_latest_price as (

    select
        j.*,

        latest.price_date,

        latest.retail_price_latest,

        case
            when latest.price_date is not null
            then j.date - latest.price_date
        end as retail_price_age_days,

        case
            when j.retail_price_observed is not null
            then true
            else false
        end as is_retail_price_observed

    from joined j

    left join lateral (

        select
            k.date as price_date,
            k.retail_price_median
                as retail_price_latest

        from kamis_daily k

        where k.product_id = j.product_id
          and k.date <= j.date

        order by k.date desc

        limit 1

    ) latest
        on true

)

select *
from with_latest_price
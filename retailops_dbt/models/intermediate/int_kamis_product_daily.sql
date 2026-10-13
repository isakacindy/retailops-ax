with kamis_source as (

    select *
    from {{ ref('stg_kamis_price') }}

),

mapping as (

    select *
    from {{ ref('product_source_mapping') }}
    where source = 'KAMIS'

),

mapped as (

    select
        k.survey_date as date,

        m.standard_product_id as product_id,
        m.standard_product_name as product_name,

        k.region_cd,
        k.region_name,

        k.market_cd,
        k.market_name,

        k.converted_price

    from kamis_source k

    inner join mapping m
        on k.item_cd = m.source_product_code

    where k.section_cd = '01'
      and k.region_cd = '1101'
      and k.variety_cd = '00'
      and k.grade_cd = '04'

),

daily as (

    select
        date,
        product_id,
        product_name,

        region_cd,
        region_name,

        count(distinct market_cd) as retail_market_count,

        avg(converted_price) as retail_price_avg,

        percentile_cont(0.5)
        within group (
            order by converted_price
        ) as retail_price_median,

        min(converted_price) as retail_price_min,

        max(converted_price) as retail_price_max,

        stddev_samp(converted_price) as retail_price_std

    from mapped

    group by
        date,
        product_id,
        product_name,
        region_cd,
        region_name

)

select *
from daily
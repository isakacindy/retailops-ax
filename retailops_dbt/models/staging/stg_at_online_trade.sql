with source as (

    select *
    from {{ source('raw', 'at_online_trade') }}

),

renamed as (

    select
        raw_id,

        trade_date,

        category_l_cd,
        category_l_name,

        category_m_cd,
        category_m_name,

        category_s_cd,

        case
            when category_s_cd = '120199'
                then '기타양파'
            else category_s_name
        end as category_s_name,

        confirmed_qty,
        avg_price,
        low_price,
        high_price,

        ingested_at

    from source

)

select *
from renamed
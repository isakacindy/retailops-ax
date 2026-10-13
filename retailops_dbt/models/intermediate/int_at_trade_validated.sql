with source as (

    select *
    from {{ ref('stg_at_online_trade') }}

),

validated as (

    select
        *,

        case
            when confirmed_qty > 5000000
              or avg_price > 100000
                then 'HARD_ANOMALY'

            when confirmed_qty > 2000000
              or avg_price > 10000
                then 'REVIEW'

            else 'OK'
        end as dq_status,

        case
            when confirmed_qty > 5000000
                then 'EXTREME_QTY'

            when avg_price > 100000
                then 'EXTREME_PRICE'

            when confirmed_qty > 2000000
                then 'HIGH_QTY_REVIEW'

            when avg_price > 10000
                then 'HIGH_PRICE_REVIEW'

            else null
        end as dq_reason

    from source

)

select *
from validated
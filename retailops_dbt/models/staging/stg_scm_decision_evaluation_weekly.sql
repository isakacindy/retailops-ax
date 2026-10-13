with source as (

    select *
    from {{ source('raw', 'scm_decision_evaluation_weekly') }}

),

renamed as (

    select
        decision_week::date
            as decision_week,

        product_id,

        decision_signal,

        baseline_order_qty_kg::numeric
            as baseline_order_qty_kg,

        recommended_order_qty_kg::numeric
            as recommended_order_qty_kg,

        order_timing_shift_kg::numeric
            as order_timing_shift_kg,

        actual_price_index::numeric
            as actual_price_index,

        actual_weekly_demand_kg::numeric
            as actual_weekly_demand_kg,

        lost_sales_kg::numeric
            as lost_sales_kg,

        fill_rate::numeric
            as fill_rate,

        actual_price_increase::boolean
            as actual_price_increase

    from source

)

select *
from renamed
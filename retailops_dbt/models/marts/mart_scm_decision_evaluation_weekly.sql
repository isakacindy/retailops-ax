with evaluation as (

    select *
    from {{ ref('stg_scm_decision_evaluation_weekly') }}

),

final as (

    select
        decision_week,
        product_id,

        decision_signal,

        baseline_order_qty_kg,
        recommended_order_qty_kg,
        order_timing_shift_kg,

        actual_price_index,
        actual_weekly_demand_kg,

        lost_sales_kg,
        fill_rate,

        actual_price_increase

    from evaluation

)

select *
from final
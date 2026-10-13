with decision as (

    select *
    from {{ ref('stg_scm_decision_engine_weekly') }}

),

final as (

    select
        decision_week,

        product_id,
        product_name,

        -- Price Risk
        current_price_index,
        forecast_price_index,

        current_risk_level,
        forecast_risk_level,

        -- Inventory / Replenishment
        beginning_inventory_kg,
        inbound_qty_kg,
        open_order_qty_kg,
        inventory_position_kg,

        forecast_weekly_demand_kg,

        lead_time_days,
        safety_stock_days,
        risk_buffer_days,

        -- Decision
        baseline_order_qty_kg,
        recommended_order_qty_kg,
        order_timing_shift_kg,

        case
            when order_timing_shift_kg > 0
                then order_timing_shift_kg
            else 0
        end as advance_order_qty_kg,

        case
            when order_timing_shift_kg < 0
                then abs(order_timing_shift_kg)
            else 0
        end as offset_reduction_qty_kg,

        ending_inventory_kg,
        ending_days_of_cover,

        decision_signal,
        decision_reason,

        -- Quality / Lineage
        has_price_forecast,
        data_quality_flag,
        policy_version,

        market_data_scope,
        enterprise_data_scope,
        decision_scope

    from decision

)

select *
from final
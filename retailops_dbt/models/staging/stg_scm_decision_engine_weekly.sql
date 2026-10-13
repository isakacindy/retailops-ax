with source as (

    select *
    from {{ source('raw', 'scm_decision_engine_weekly') }}

),

renamed as (

    select
        decision_week::date
            as decision_week,

        product_id,
        product_name,

        market_data_scope,
        enterprise_data_scope,
        decision_scope,

        current_price_index::numeric
            as current_price_index,

        forecast_price_index::numeric
            as forecast_price_index,

        current_risk_level,
        forecast_risk_level,

        has_price_forecast::boolean
            as has_price_forecast,

        beginning_inventory_kg::numeric
            as beginning_inventory_kg,

        inbound_qty_kg::numeric
            as inbound_qty_kg,

        open_order_qty_kg::numeric
            as open_order_qty_kg,

        inventory_position_kg::numeric
            as inventory_position_kg,

        forecast_weekly_demand_kg::numeric
            as forecast_weekly_demand_kg,

        lead_time_days::integer
            as lead_time_days,

        safety_stock_days::integer
            as safety_stock_days,

        risk_buffer_days::integer
            as risk_buffer_days,

        baseline_order_qty_kg::numeric
            as baseline_order_qty_kg,

        recommended_order_qty_kg::numeric
            as recommended_order_qty_kg,

        order_timing_shift_kg::numeric
            as order_timing_shift_kg,

        ending_inventory_kg::numeric
            as ending_inventory_kg,

        ending_days_of_cover::numeric
            as ending_days_of_cover,

        decision_signal,
        decision_reason,

        data_quality_flag,
        policy_version

    from source

)

select *
from renamed
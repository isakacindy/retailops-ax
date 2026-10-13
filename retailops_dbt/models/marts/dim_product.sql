with mapping as (

    select *
    from {{ ref('product_source_mapping') }}

),

products as (

    select distinct
        standard_product_id as product_id,
        standard_product_name as product_name

    from mapping

)

select *
from products
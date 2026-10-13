select
    decision_week,
    product_id,
    count(*) as row_count

from {{ ref('mart_scm_decision_weekly') }}

group by
    decision_week,
    product_id

having count(*) > 1
select 1
from {{ ref('mart_scm_decision_weekly') }}
where false
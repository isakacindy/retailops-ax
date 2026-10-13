with source as (

    select *
    from {{ source('raw', 'kamis_price') }}

),

renamed as (

    select
        raw_id,

        survey_date,

        section_cd,
        section_name,

        category_cd,
        category_name,

        item_cd,
        item_name,

        variety_cd,
        variety_name,

        grade_cd,
        grade_name,

        region_cd,
        region_name,

        market_cd,
        market_name,

        unit,
        unit_size,

        survey_price,
        converted_price,

        source_registered_at,
        ingested_at

    from source

)

select *
from renamed
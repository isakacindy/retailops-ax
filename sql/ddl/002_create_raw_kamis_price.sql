CREATE TABLE IF NOT EXISTS raw.kamis_price (
    raw_id BIGSERIAL PRIMARY KEY,

    survey_date DATE NOT NULL,

    section_cd VARCHAR(10) NOT NULL,
    section_name VARCHAR(50),

    category_cd VARCHAR(10) NOT NULL,
    category_name VARCHAR(100),

    item_cd VARCHAR(10) NOT NULL,
    item_name VARCHAR(100),

    variety_cd VARCHAR(10) NOT NULL,
    variety_name VARCHAR(100),

    grade_cd VARCHAR(10) NOT NULL,
    grade_name VARCHAR(50),

    region_cd VARCHAR(10) NOT NULL,
    region_name VARCHAR(100),

    market_cd VARCHAR(20) NOT NULL,
    market_name VARCHAR(100),

    unit VARCHAR(20) NOT NULL,
    unit_size NUMERIC(18, 3) NOT NULL,

    survey_price NUMERIC(18, 3),
    converted_price NUMERIC(18, 3),

    source_registered_at TIMESTAMPTZ,

    ingested_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE (
        survey_date,
        section_cd,
        item_cd,
        variety_cd,
        grade_cd,
        region_cd,
        market_cd,
        unit,
        unit_size
    )
);
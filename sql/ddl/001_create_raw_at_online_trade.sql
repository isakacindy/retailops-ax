CREATE SCHEMA IF NOT EXISTS raw;

CREATE TABLE IF NOT EXISTS raw.at_online_trade (
    raw_id BIGSERIAL PRIMARY KEY,

    trade_date DATE NOT NULL,

    category_l_cd VARCHAR(10) NOT NULL,
    category_l_name VARCHAR(100),

    category_m_cd VARCHAR(10) NOT NULL,
    category_m_name VARCHAR(100),

    category_s_cd VARCHAR(10) NOT NULL,
    category_s_name VARCHAR(100),

    confirmed_qty NUMERIC(18, 3),
    avg_price NUMERIC(18, 3),
    low_price NUMERIC(18, 3),
    high_price NUMERIC(18, 3),

    ingested_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE (trade_date, category_s_cd)
);
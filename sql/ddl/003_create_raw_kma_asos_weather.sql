create schema if not exists raw;

create table if not exists raw.kma_asos_weather (

    weather_date date not null,

    station_id varchar(10) not null,
    station_name varchar(50) not null,

    region_code varchar(30) not null,

    avg_temp_c numeric(8, 3),
    min_temp_c numeric(8, 3),
    max_temp_c numeric(8, 3),

    precipitation_mm numeric(10, 3),

    avg_humidity_pct numeric(8, 3),

    sunshine_hours numeric(8, 3),
    solar_radiation_mj_m2 numeric(10, 3),

    avg_wind_speed_m_s numeric(8, 3),

    ingested_at timestamptz not null default now(),

    constraint uq_kma_asos_weather
        unique (
            weather_date,
            station_id
        )
);
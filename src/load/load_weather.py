import os
from pathlib import Path

import pandas as pd
import psycopg2

from dotenv import load_dotenv
from psycopg2.extras import execute_values


# 환경변수
load_dotenv()


DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "dbname": os.getenv("DB_NAME", "retailops_ax"),
    "user": os.getenv("DB_USER", "cindy"),
}

db_password = os.getenv("DB_PASSWORD")

if db_password:
    DB_CONFIG["password"] = db_password


# 파일
CSV_PATH = Path(
    "data/raw/kma_asos_onion_regions_raw.csv"
)

if not CSV_PATH.exists():
    raise FileNotFoundError(
        f"파일을 찾을 수 없습니다: {CSV_PATH}"
    )


# CSV 읽기
df = pd.read_csv(
    CSV_PATH,
    dtype={
        "station_id": str,
        "station_name": str,
        "region_code": str,
    }
)

df["weather_date"] = pd.to_datetime(
    df["weather_date"],
    errors="raise"
).dt.date


numeric_columns = [
    "avg_temp_c",
    "min_temp_c",
    "max_temp_c",
    "precipitation_mm",
    "avg_humidity_pct",
    "sunshine_hours",
    "solar_radiation_mj_m2",
    "avg_wind_speed_m_s",
]

for column in numeric_columns:
    df[column] = pd.to_numeric(
        df[column],
        errors="coerce"
    )


# Grain 검증
duplicate_count = (
    df.duplicated(
        subset=[
            "weather_date",
            "station_id"
        ]
    )
    .sum()
)

if duplicate_count > 0:
    raise ValueError(
        f"weather_date × station_id "
        f"중복 {duplicate_count}건 발견"
    )


# NaN → None 변환 helper
def clean_value(value):

    if pd.isna(value):
        return None

    return value


rows = []

for row in df.itertuples(index=False):

    rows.append(
        (
            row.weather_date,

            row.station_id,
            row.station_name,
            row.region_code,

            clean_value(row.avg_temp_c),
            clean_value(row.min_temp_c),
            clean_value(row.max_temp_c),

            clean_value(row.precipitation_mm),

            clean_value(row.avg_humidity_pct),

            clean_value(row.sunshine_hours),
            clean_value(row.solar_radiation_mj_m2),

            clean_value(row.avg_wind_speed_m_s),
        )
    )


# UPSERT
sql = """
insert into raw.kma_asos_weather (

    weather_date,

    station_id,
    station_name,
    region_code,

    avg_temp_c,
    min_temp_c,
    max_temp_c,

    precipitation_mm,

    avg_humidity_pct,

    sunshine_hours,
    solar_radiation_mj_m2,

    avg_wind_speed_m_s

)
values %s

on conflict (
    weather_date,
    station_id
)

do update set

    station_name = excluded.station_name,
    region_code = excluded.region_code,

    avg_temp_c = excluded.avg_temp_c,
    min_temp_c = excluded.min_temp_c,
    max_temp_c = excluded.max_temp_c,

    precipitation_mm = excluded.precipitation_mm,

    avg_humidity_pct = excluded.avg_humidity_pct,

    sunshine_hours = excluded.sunshine_hours,
    solar_radiation_mj_m2 =
        excluded.solar_radiation_mj_m2,

    avg_wind_speed_m_s =
        excluded.avg_wind_speed_m_s,

    ingested_at = now()
"""


connection = psycopg2.connect(
    **DB_CONFIG
)

try:

    with connection.cursor() as cursor:

        execute_values(
            cursor,
            sql,
            rows,
            page_size=1000
        )

    connection.commit()

finally:
    connection.close()


print(
    f"Weather load complete: "
    f"{len(rows):,} rows processed"
)


# 적재 검증
connection = psycopg2.connect(
    **DB_CONFIG
)

try:

    validation_query = """
    select
        station_id,
        station_name,
        region_code,

        count(*) as rows,

        min(weather_date) as min_date,
        max(weather_date) as max_date

    from raw.kma_asos_weather

    group by
        station_id,
        station_name,
        region_code

    order by station_id
    """

    validation_df = pd.read_sql(
        validation_query,
        connection
    )

finally:
    connection.close()


print()
print(validation_df)
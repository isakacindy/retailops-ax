import os
from pathlib import Path

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CSV_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "kamis_onion_seoul_raw.csv"
)

load_dotenv(PROJECT_ROOT / ".env")


def get_connection():
    params = {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": os.getenv("DB_PORT", "5432"),
        "dbname": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
    }

    password = os.getenv("DB_PASSWORD")

    if password:
        params["password"] = password

    return psycopg2.connect(**params)


def read_raw_csv():
    if not CSV_PATH.exists():
        raise FileNotFoundError(
            f"CSV 파일을 찾을 수 없습니다: {CSV_PATH}"
        )

    df = pd.read_csv(
        CSV_PATH,
        dtype={
            "se_cd": str,
            "ctgry_cd": str,
            "item_cd": str,
            "vrty_cd": str,
            "grd_cd": str,
            "sgg_cd": str,
            "mrkt_cd": str,
        }
    )

    return df


def prepare_dataframe(df):
    df = df.copy()

    df["exmn_ymd"] = pd.to_datetime(
        df["exmn_ymd"],
        format="%Y-%m-%d",
        errors="raise"
    ).dt.date

    df["orgnl_reg_dt"] = pd.to_datetime(
        df["orgnl_reg_dt"],
        utc=True,
        errors="raise"
    )

    numeric_cols = [
        "unit_sz",
        "exmn_dd_prc",
        "exmn_dd_cnvs_prc",
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(
            df[col],
            errors="raise"
        )

    grain_cols = [
        "exmn_ymd",
        "se_cd",
        "item_cd",
        "vrty_cd",
        "grd_cd",
        "sgg_cd",
        "mrkt_cd",
        "unit",
        "unit_sz",
    ]

    duplicate_count = df.duplicated(
        subset=grain_cols
    ).sum()

    if duplicate_count > 0:
        raise ValueError(
            f"Grain 중복 발견: {duplicate_count}건"
        )

    return df


def dataframe_to_records(df):
    records = []

    for row in df.itertuples(index=False):
        records.append(
            (
                row.exmn_ymd,

                row.se_cd,
                row.se_nm,

                row.ctgry_cd,
                row.ctgry_nm,

                row.item_cd,
                row.item_nm,

                row.vrty_cd,
                row.vrty_nm,

                row.grd_cd,
                row.grd_nm,

                row.sgg_cd,
                row.sgg_nm,

                row.mrkt_cd,
                row.mrkt_nm,

                row.unit,
                float(row.unit_sz),

                float(row.exmn_dd_prc),
                float(row.exmn_dd_cnvs_prc),

                row.orgnl_reg_dt,
            )
        )

    return records


def upsert_raw_data(conn, records):
    sql = """
        INSERT INTO raw.kamis_price (
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

            source_registered_at
        )

        VALUES %s

        ON CONFLICT (
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

        DO UPDATE SET

            section_name =
                EXCLUDED.section_name,

            category_name =
                EXCLUDED.category_name,

            item_name =
                EXCLUDED.item_name,

            variety_name =
                EXCLUDED.variety_name,

            grade_name =
                EXCLUDED.grade_name,

            region_name =
                EXCLUDED.region_name,

            market_name =
                EXCLUDED.market_name,

            survey_price =
                EXCLUDED.survey_price,

            converted_price =
                EXCLUDED.converted_price,

            source_registered_at =
                EXCLUDED.source_registered_at,

            ingested_at =
                CURRENT_TIMESTAMP;
    """

    with conn.cursor() as cursor:
        execute_values(
            cursor,
            sql,
            records,
            page_size=500
        )


def print_summary(conn):
    sql = """
        SELECT
            COUNT(*),
            MIN(survey_date),
            MAX(survey_date),
            COUNT(DISTINCT market_cd)
        FROM raw.kamis_price
        WHERE item_cd = '245';
    """

    with conn.cursor() as cursor:
        cursor.execute(sql)
        count, min_date, max_date, markets = cursor.fetchone()

    print("\n===== DB SUMMARY =====")
    print(f"양파 데이터: {count:,}건")
    print(f"기간: {min_date} ~ {max_date}")
    print(f"시장 수: {markets}")


def main():
    print("===== KAMIS RAW LOAD START =====")

    df = read_raw_csv()

    print(f"CSV 읽기 완료: {len(df):,}건")

    df = prepare_dataframe(df)

    print("데이터 검증 완료")

    records = dataframe_to_records(df)

    conn = None

    try:
        conn = get_connection()

        print("PostgreSQL 연결 완료")

        upsert_raw_data(
            conn,
            records
        )

        conn.commit()

        print(
            f"UPSERT 완료: {len(records):,}건 처리"
        )

        print_summary(conn)

    except Exception:
        if conn:
            conn.rollback()
        raise

    finally:
        if conn:
            conn.close()

        print("\nPostgreSQL 연결 종료")


if __name__ == "__main__":
    main()
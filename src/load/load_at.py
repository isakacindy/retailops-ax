import os
from pathlib import Path

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv


# Path / Environment
PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_PATH = PROJECT_ROOT / ".env"
CSV_PATH = PROJECT_ROOT / "data" / "raw" / "at_onion_raw.csv"

load_dotenv(ENV_PATH)


# Database Connection
def get_connection():
    conn_params = {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": os.getenv("DB_PORT", "5432"),
        "dbname": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
    }

    # 비밀번호를 설정한 환경에서만 사용
    password = os.getenv("DB_PASSWORD")

    if password:
        conn_params["password"] = password

    return psycopg2.connect(**conn_params)


# Read & Validate
def read_raw_csv():
    if not CSV_PATH.exists():
        raise FileNotFoundError(
            f"RAW CSV를 찾을 수 없습니다: {CSV_PATH}"
        )

    df = pd.read_csv(CSV_PATH)

    required_columns = [
        "cfmtn_ymd",
        "onln_whsl_mrkt_lclsf_cd",
        "onln_whsl_mrkt_lclsf_nm",
        "onln_whsl_mrkt_mclsf_cd",
        "onln_whsl_mrkt_mclsf_nm",
        "onln_whsl_mrkt_sclsf_cd",
        "onln_whsl_mrkt_sclsf_nm",
        "cfmtn_qty",
        "avgprc",
        "lwprc",
        "hgprc",
    ]

    missing_columns = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"필수 컬럼 누락: {missing_columns}"
        )

    return df


# Transform for DB Load
def prepare_dataframe(df):
    df = df.copy()

    # 날짜
    df["cfmtn_ymd"] = pd.to_datetime(
        df["cfmtn_ymd"],
        errors="raise"
    ).dt.date

    # 코드값은 문자열 유지
    code_columns = [
        "onln_whsl_mrkt_lclsf_cd",
        "onln_whsl_mrkt_mclsf_cd",
        "onln_whsl_mrkt_sclsf_cd",
    ]

    for col in code_columns:
        df[col] = df[col].astype(str).str.zfill(
            {
                "onln_whsl_mrkt_lclsf_cd": 2,
                "onln_whsl_mrkt_mclsf_cd": 4,
                "onln_whsl_mrkt_sclsf_cd": 6,
            }[col]
        )

    # 숫자형
    numeric_columns = [
        "cfmtn_qty",
        "avgprc",
        "lwprc",
        "hgprc",
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(
            df[col],
            errors="raise"
        )

    # Grain 검증
    duplicate_count = df.duplicated(
        subset=[
            "cfmtn_ymd",
            "onln_whsl_mrkt_sclsf_cd"
        ]
    ).sum()

    if duplicate_count > 0:
        raise ValueError(
            f"Grain 중복 발견: {duplicate_count}건"
        )

    return df


# Convert to DB Records
def dataframe_to_records(df):
    records = []

    for row in df.itertuples(index=False):
        records.append(
            (
                row.cfmtn_ymd,

                str(row.onln_whsl_mrkt_lclsf_cd),
                row.onln_whsl_mrkt_lclsf_nm,

                str(row.onln_whsl_mrkt_mclsf_cd),
                row.onln_whsl_mrkt_mclsf_nm,

                str(row.onln_whsl_mrkt_sclsf_cd),
                row.onln_whsl_mrkt_sclsf_nm,

                float(row.cfmtn_qty),
                float(row.avgprc),
                float(row.lwprc),
                float(row.hgprc),
            )
        )

    return records


# Load / Upsert
def upsert_raw_data(conn, records):
    sql = """
        INSERT INTO raw.at_online_trade (
            trade_date,

            category_l_cd,
            category_l_name,

            category_m_cd,
            category_m_name,

            category_s_cd,
            category_s_name,

            confirmed_qty,
            avg_price,
            low_price,
            high_price
        )
        VALUES %s

        ON CONFLICT (
            trade_date,
            category_s_cd
        )
        DO UPDATE SET

            category_l_cd =
                EXCLUDED.category_l_cd,

            category_l_name =
                EXCLUDED.category_l_name,

            category_m_cd =
                EXCLUDED.category_m_cd,

            category_m_name =
                EXCLUDED.category_m_name,

            category_s_name =
                EXCLUDED.category_s_name,

            confirmed_qty =
                EXCLUDED.confirmed_qty,

            avg_price =
                EXCLUDED.avg_price,

            low_price =
                EXCLUDED.low_price,

            high_price =
                EXCLUDED.high_price,

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


# Validation
def print_db_summary(conn):
    sql = """
        SELECT
            COUNT(*) AS row_count,
            MIN(trade_date) AS min_date,
            MAX(trade_date) AS max_date
        FROM raw.at_online_trade
        WHERE category_m_cd = '1201';
    """

    with conn.cursor() as cursor:
        cursor.execute(sql)
        row_count, min_date, max_date = cursor.fetchone()

    print("\n===== DB SUMMARY =====")
    print(f"양파 데이터 건수: {row_count}")
    print(f"기간: {min_date} ~ {max_date}")


# Main
def main():

    print("===== AT RAW LOAD START =====")

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

        print_db_summary(conn)

    except Exception as e:

        if conn:
            conn.rollback()

        print(f"\nLOAD 실패: {e}")

        raise

    finally:

        if conn:
            conn.close()

        print("\nPostgreSQL 연결 종료")


if __name__ == "__main__":
    main()
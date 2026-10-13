# src/load/load_decision_outputs.py

from pathlib import Path
from importlib.util import find_spec
import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL


# =========================================================
# 1. Project Paths
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

ENV_PATH = PROJECT_ROOT / ".env"

DATA_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
)

DECISION_CSV = (
    DATA_DIR
    / "scm_decision_engine_weekly.csv"
)

EVALUATION_CSV = (
    DATA_DIR
    / "scm_decision_evaluation_weekly.csv"
)


# =========================================================
# 2. Environment Variables
# =========================================================

load_dotenv(ENV_PATH)


def get_env(*names, default=None):
    """
    여러 환경변수명 중 먼저 존재하는 값을 반환한다.

    예:
    DB_HOST 또는 POSTGRES_HOST
    """
    for name in names:
        value = os.getenv(name)

        if value not in (None, ""):
            return value

    return default


DB_HOST = get_env(
    "DB_HOST",
    "POSTGRES_HOST",
    default="localhost",
)

DB_PORT = get_env(
    "DB_PORT",
    "POSTGRES_PORT",
    default="5432",
)

DB_NAME = get_env(
    "DB_NAME",
    "POSTGRES_DB",
    default="retailops_ax",
)

DB_USER = get_env(
    "DB_USER",
    "POSTGRES_USER",
)

DB_PASSWORD = get_env(
    "DB_PASSWORD",
    "POSTGRES_PASSWORD",
)


# =========================================================
# 3. Configuration Validation
# =========================================================

def validate_configuration():

    if not ENV_PATH.exists():
        raise FileNotFoundError(
            f".env 파일을 찾을 수 없습니다: {ENV_PATH}"
        )

    if DB_USER is None:
        raise ValueError(
            "DB_USER 또는 POSTGRES_USER가 "
            ".env에 설정되어 있지 않습니다."
        )

    if not DECISION_CSV.exists():
        raise FileNotFoundError(
            f"Decision CSV를 찾을 수 없습니다:\n"
            f"{DECISION_CSV}"
        )

    if not EVALUATION_CSV.exists():
        raise FileNotFoundError(
            f"Evaluation CSV를 찾을 수 없습니다:\n"
            f"{EVALUATION_CSV}"
        )


# =========================================================
# 4. PostgreSQL Driver
# =========================================================

def get_postgres_driver():
    """
    설치된 PostgreSQL 드라이버를 자동으로 선택한다.

    우선순위:
    1. psycopg (v3)
    2. psycopg2
    """

    if find_spec("psycopg") is not None:
        return "postgresql+psycopg"

    if find_spec("psycopg2") is not None:
        return "postgresql+psycopg2"

    raise ImportError(
        "PostgreSQL 드라이버가 설치되어 있지 않습니다.\n"
        "다음 중 하나를 설치하세요:\n"
        "pip install psycopg[binary]\n"
        "또는\n"
        "pip install psycopg2-binary"
    )


# =========================================================
# 5. Database Engine
# =========================================================

def create_db_engine():

    driver = get_postgres_driver()

    database_url = URL.create(
        drivername=driver,
        username=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=int(DB_PORT),
        database=DB_NAME,
    )

    engine = create_engine(
        database_url,
        pool_pre_ping=True,
    )

    return engine


# =========================================================
# 6. Read Decision Outputs
# =========================================================

def load_csv_files():

    decision_df = pd.read_csv(
        DECISION_CSV,
        parse_dates=["decision_week"],
    )

    evaluation_df = pd.read_csv(
        EVALUATION_CSV,
        parse_dates=["decision_week"],
    )

    return decision_df, evaluation_df


# =========================================================
# 7. Data Validation
# =========================================================

def validate_decision_data(
    decision_df,
    evaluation_df,
):

    # -----------------------------------------------------
    # Required Columns
    # -----------------------------------------------------

    required_decision_columns = [
        "decision_week",
        "product_id",
        "product_name",
        "market_data_scope",
        "enterprise_data_scope",
        "decision_scope",
        "current_price_index",
        "forecast_price_index",
        "current_risk_level",
        "forecast_risk_level",
        "has_price_forecast",
        "beginning_inventory_kg",
        "inbound_qty_kg",
        "open_order_qty_kg",
        "inventory_position_kg",
        "forecast_weekly_demand_kg",
        "lead_time_days",
        "safety_stock_days",
        "risk_buffer_days",
        "baseline_order_qty_kg",
        "recommended_order_qty_kg",
        "order_timing_shift_kg",
        "ending_inventory_kg",
        "ending_days_of_cover",
        "decision_signal",
        "decision_reason",
        "data_quality_flag",
        "policy_version",
    ]

    required_evaluation_columns = [
        "decision_week",
        "product_id",
        "decision_signal",
        "baseline_order_qty_kg",
        "recommended_order_qty_kg",
        "order_timing_shift_kg",
        "actual_price_index",
        "actual_weekly_demand_kg",
        "lost_sales_kg",
        "fill_rate",
        "actual_price_increase",
    ]

    missing_decision_columns = [
        col
        for col in required_decision_columns
        if col not in decision_df.columns
    ]

    missing_evaluation_columns = [
        col
        for col in required_evaluation_columns
        if col not in evaluation_df.columns
    ]

    if missing_decision_columns:
        raise ValueError(
            "Decision CSV에 필요한 컬럼이 없습니다:\n"
            f"{missing_decision_columns}"
        )

    if missing_evaluation_columns:
        raise ValueError(
            "Evaluation CSV에 필요한 컬럼이 없습니다:\n"
            f"{missing_evaluation_columns}"
        )

    # -----------------------------------------------------
    # Empty Data
    # -----------------------------------------------------

    if decision_df.empty:
        raise ValueError(
            "Decision CSV가 비어 있습니다."
        )

    if evaluation_df.empty:
        raise ValueError(
            "Evaluation CSV가 비어 있습니다."
        )

    # -----------------------------------------------------
    # Row Count Alignment
    # -----------------------------------------------------

    if len(decision_df) != len(evaluation_df):
        raise ValueError(
            "Decision / Evaluation row 수가 다릅니다.\n"
            f"Decision: {len(decision_df)}\n"
            f"Evaluation: {len(evaluation_df)}"
        )

    # -----------------------------------------------------
    # Key Validation
    # -----------------------------------------------------

    decision_duplicate_count = (
        decision_df
        .duplicated(
            subset=[
                "decision_week",
                "product_id",
            ]
        )
        .sum()
    )

    evaluation_duplicate_count = (
        evaluation_df
        .duplicated(
            subset=[
                "decision_week",
                "product_id",
            ]
        )
        .sum()
    )

    if decision_duplicate_count > 0:
        raise ValueError(
            "Decision CSV에 중복 Key가 존재합니다.\n"
            f"중복 건수: {decision_duplicate_count}"
        )

    if evaluation_duplicate_count > 0:
        raise ValueError(
            "Evaluation CSV에 중복 Key가 존재합니다.\n"
            f"중복 건수: {evaluation_duplicate_count}"
        )

    # -----------------------------------------------------
    # Null Key Validation
    # -----------------------------------------------------

    if (
        decision_df[
            [
                "decision_week",
                "product_id",
            ]
        ]
        .isna()
        .any()
        .any()
    ):
        raise ValueError(
            "Decision CSV의 Key 컬럼에 NULL이 있습니다."
        )

    if (
        evaluation_df[
            [
                "decision_week",
                "product_id",
            ]
        ]
        .isna()
        .any()
        .any()
    ):
        raise ValueError(
            "Evaluation CSV의 Key 컬럼에 NULL이 있습니다."
        )

    # -----------------------------------------------------
    # Scope Validation
    # -----------------------------------------------------

    invalid_market_scope = (
        decision_df[
            "market_data_scope"
        ]
        .dropna()
        .ne("PUBLIC_ACTUAL")
        .any()
    )

    if invalid_market_scope:
        raise ValueError(
            "market_data_scope에 "
            "PUBLIC_ACTUAL 이외의 값이 있습니다."
        )

    invalid_enterprise_scope = (
        decision_df[
            "enterprise_data_scope"
        ]
        .dropna()
        .ne("SIMULATED")
        .any()
    )

    if invalid_enterprise_scope:
        raise ValueError(
            "enterprise_data_scope에 "
            "SIMULATED 이외의 값이 있습니다."
        )

    # -----------------------------------------------------
    # Date Range Alignment
    # -----------------------------------------------------

    decision_keys = set(
        zip(
            decision_df["decision_week"],
            decision_df["product_id"],
        )
    )

    evaluation_keys = set(
        zip(
            evaluation_df["decision_week"],
            evaluation_df["product_id"],
        )
    )

    if decision_keys != evaluation_keys:
        raise ValueError(
            "Decision / Evaluation의 "
            "decision_week × product_id Key가 일치하지 않습니다."
        )

    print("[OK] CSV validation passed")
    print(
        f"  Decision rows   : {len(decision_df):,}"
    )
    print(
        f"  Evaluation rows : {len(evaluation_df):,}"
    )
    print(
        "  Decision period : "
        f"{decision_df['decision_week'].min().date()} "
        f"~ "
        f"{decision_df['decision_week'].max().date()}"
    )


# =========================================================
# 8. Create RAW Schema
# =========================================================

def create_raw_schema(engine):

    with engine.begin() as conn:

        conn.execute(
            text(
                """
                CREATE SCHEMA IF NOT EXISTS raw
                """
            )
        )

    print("[OK] raw schema ready")


# =========================================================
# 9. Load Tables
# =========================================================

def load_to_postgres(
    engine,
    decision_df,
    evaluation_df,
):

    with engine.begin() as conn:

        # =================================================
        # Decision Table
        # =================================================

        decision_table_exists = conn.execute(
            text(
                """
                SELECT EXISTS (
                    SELECT 1
                    FROM information_schema.tables
                    WHERE table_schema = 'raw'
                      AND table_name = 'scm_decision_engine_weekly'
                )
                """
            )
        ).scalar_one()

        if decision_table_exists:

            conn.execute(
                text(
                    """
                    TRUNCATE TABLE
                        raw.scm_decision_engine_weekly
                    """
                )
            )

            decision_df.to_sql(
                name="scm_decision_engine_weekly",
                con=conn,
                schema="raw",
                if_exists="append",
                index=False,
                method="multi",
            )

        else:

            decision_df.to_sql(
                name="scm_decision_engine_weekly",
                con=conn,
                schema="raw",
                if_exists="append",
                index=False,
                method="multi",
            )


        # =================================================
        # Evaluation Table
        # =================================================

        evaluation_table_exists = conn.execute(
            text(
                """
                SELECT EXISTS (
                    SELECT 1
                    FROM information_schema.tables
                    WHERE table_schema = 'raw'
                      AND table_name = 'scm_decision_evaluation_weekly'
                )
                """
            )
        ).scalar_one()

        if evaluation_table_exists:

            conn.execute(
                text(
                    """
                    TRUNCATE TABLE
                        raw.scm_decision_evaluation_weekly
                    """
                )
            )

            evaluation_df.to_sql(
                name="scm_decision_evaluation_weekly",
                con=conn,
                schema="raw",
                if_exists="append",
                index=False,
                method="multi",
            )

        else:

            evaluation_df.to_sql(
                name="scm_decision_evaluation_weekly",
                con=conn,
                schema="raw",
                if_exists="append",
                index=False,
                method="multi",
            )


    print(
        "[OK] raw.scm_decision_engine_weekly loaded"
    )

    print(
        "[OK] raw.scm_decision_evaluation_weekly loaded"
    )


# =========================================================
# 10. Database Validation
# =========================================================

def validate_database(
    engine,
    expected_decision_rows,
    expected_evaluation_rows,
):

    with engine.connect() as conn:

        decision_count = conn.execute(
            text(
                """
                SELECT COUNT(*)
                FROM raw.scm_decision_engine_weekly
                """
            )
        ).scalar_one()

        evaluation_count = conn.execute(
            text(
                """
                SELECT COUNT(*)
                FROM raw.scm_decision_evaluation_weekly
                """
            )
        ).scalar_one()

        decision_duplicate_count = conn.execute(
            text(
                """
                SELECT COUNT(*)
                FROM (
                    SELECT
                        decision_week,
                        product_id
                    FROM raw.scm_decision_engine_weekly
                    GROUP BY
                        decision_week,
                        product_id
                    HAVING COUNT(*) > 1
                ) t
                """
            )
        ).scalar_one()

        evaluation_duplicate_count = conn.execute(
            text(
                """
                SELECT COUNT(*)
                FROM (
                    SELECT
                        decision_week,
                        product_id
                    FROM raw.scm_decision_evaluation_weekly
                    GROUP BY
                        decision_week,
                        product_id
                    HAVING COUNT(*) > 1
                ) t
                """
            )
        ).scalar_one()

    if decision_count != expected_decision_rows:
        raise ValueError(
            "Decision DB row 수가 CSV와 다릅니다.\n"
            f"CSV: {expected_decision_rows}\n"
            f"DB: {decision_count}"
        )

    if evaluation_count != expected_evaluation_rows:
        raise ValueError(
            "Evaluation DB row 수가 CSV와 다릅니다.\n"
            f"CSV: {expected_evaluation_rows}\n"
            f"DB: {evaluation_count}"
        )

    if decision_duplicate_count > 0:
        raise ValueError(
            "DB Decision Table에 중복 Key가 있습니다."
        )

    if evaluation_duplicate_count > 0:
        raise ValueError(
            "DB Evaluation Table에 중복 Key가 있습니다."
        )

    print()
    print("=========================================")
    print("Database Load Validation")
    print("=========================================")

    print(
        "Decision rows   :",
        decision_count,
    )

    print(
        "Evaluation rows :",
        evaluation_count,
    )

    print(
        "Decision duplicate keys   :",
        decision_duplicate_count,
    )

    print(
        "Evaluation duplicate keys :",
        evaluation_duplicate_count,
    )

    print("=========================================")
    print("[SUCCESS] Decision outputs loaded")
    print("=========================================")


# =========================================================
# 11. Main
# =========================================================

def main():

    print()
    print("=========================================")
    print("RetailOps AX — Decision Output Loader")
    print("=========================================")

    print(
        "Project root:",
        PROJECT_ROOT,
    )

    print(
        "Decision CSV:",
        DECISION_CSV,
    )

    print(
        "Evaluation CSV:",
        EVALUATION_CSV,
    )

    print(
        "Database:",
        f"{DB_HOST}:{DB_PORT}/{DB_NAME}",
    )

    print()

    # 1. Config / File validation
    validate_configuration()

    # 2. Read CSV
    decision_df, evaluation_df = (
        load_csv_files()
    )

    # 3. Data validation
    validate_decision_data(
        decision_df,
        evaluation_df,
    )

    # 4. DB connection
    engine = create_db_engine()

    # Connection test
    with engine.connect() as conn:
        conn.execute(
            text("SELECT 1")
        )

    print("[OK] PostgreSQL connection")

    # 5. Schema
    create_raw_schema(
        engine
    )

    # 6. Load
    load_to_postgres(
        engine,
        decision_df,
        evaluation_df,
    )

    # 7. Verify
    validate_database(
        engine=engine,
        expected_decision_rows=len(
            decision_df
        ),
        expected_evaluation_rows=len(
            evaluation_df
        ),
    )

    engine.dispose()


if __name__ == "__main__":
    main()
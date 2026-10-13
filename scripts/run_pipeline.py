# scripts/run_pipeline.py

from pathlib import Path
from time import perf_counter
import argparse
import os
import subprocess
import sys

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL


# =========================================================
# 1. Project Paths
# =========================================================

PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[1]
)

DBT_DIR = (
    PROJECT_ROOT
    / "retailops_dbt"
)

DATA_DIR = (
    PROJECT_ROOT
    / "data"
)

PROCESSED_DIR = (
    DATA_DIR
    / "processed"
)

NOTEBOOK_DIR = (
    PROJECT_ROOT
    / "notebooks"
)

ENV_PATH = (
    PROJECT_ROOT
    / ".env"
)


# =========================================================
# 2. Existing Scripts
# =========================================================

EXTRACT_SCRIPTS = [
    PROJECT_ROOT
    / "src"
    / "extract"
    / "extract_at.py",

    PROJECT_ROOT
    / "src"
    / "extract"
    / "extract_kamis.py",

    PROJECT_ROOT
    / "src"
    / "extract"
    / "extract_weather.py",
]


LOAD_SCRIPTS = [
    PROJECT_ROOT
    / "src"
    / "load"
    / "load_at.py",

    PROJECT_ROOT
    / "src"
    / "load"
    / "load_kamis.py",

    PROJECT_ROOT
    / "src"
    / "load"
    / "load_weather.py",
]


DECISION_LOADER = (
    PROJECT_ROOT
    / "src"
    / "load"
    / "load_decision_outputs.py"
)


# =========================================================
# 3. Notebooks
# =========================================================

RISK_MODEL_NOTEBOOK = (
    NOTEBOOK_DIR
    / "03_risk_model_validation.ipynb"
)

DECISION_NOTEBOOK = (
    NOTEBOOK_DIR
    / "04_scm_decision_simulation.ipynb"
)

BRIEF_NOTEBOOK = (
    NOTEBOOK_DIR
    / "05_scm_decision_brief.ipynb"
)


# =========================================================
# 4. Expected Outputs
# =========================================================

PRICE_RISK_OUTPUT = (
    PROCESSED_DIR
    / "price_risk_oof_predictions.csv"
)

DECISION_OUTPUT = (
    PROCESSED_DIR
    / "scm_decision_engine_weekly.csv"
)

EVALUATION_OUTPUT = (
    PROCESSED_DIR
    / "scm_decision_evaluation_weekly.csv"
)


# =========================================================
# 5. Environment
# =========================================================

load_dotenv(
    ENV_PATH
)


def get_env(
    *names,
    default=None,
):

    for name in names:

        value = os.getenv(
            name
        )

        if value not in (
            None,
            "",
        ):

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
# 6. Logging
# =========================================================

def print_header(
    text,
):

    print()
    print("=" * 68)
    print(text)
    print("=" * 68)


def print_step(
    number,
    total,
    text,
):

    print()
    print("-" * 68)
    print(
        f"[{number}/{total}] "
        f"{text}"
    )
    print("-" * 68)


# =========================================================
# 7. Command Runner
# =========================================================

def run_command(
    command,
    cwd=PROJECT_ROOT,
):

    print(
        "$",
        " ".join(
            map(
                str,
                command,
            )
        ),
    )

    start = (
        perf_counter()
    )

    result = (
        subprocess.run(
            command,
            cwd=cwd,
            check=False,
        )
    )

    elapsed = (
        perf_counter()
        - start
    )

    if (
        result.returncode
        != 0
    ):

        raise RuntimeError(
            "\nCommand failed.\n"
            f"Exit code: {result.returncode}\n"
            f"Command: {' '.join(map(str, command))}"
        )

    print(
        f"[OK] "
        f"{elapsed:.1f}s"
    )


# =========================================================
# 8. File Validation
# =========================================================

def require_file(
    path,
):

    if not path.exists():

        raise FileNotFoundError(
            f"필수 파일을 찾을 수 없습니다:\n"
            f"{path}"
        )


def validate_project_structure():

    print_header(
        "Project Structure Validation"
    )

    require_file(
        ENV_PATH
    )

    require_file(
        DECISION_LOADER
    )

    for path in (
        EXTRACT_SCRIPTS
        + LOAD_SCRIPTS
    ):

        require_file(
            path
        )

    require_file(
        RISK_MODEL_NOTEBOOK
    )

    require_file(
        DECISION_NOTEBOOK
    )

    if not DBT_DIR.exists():

        raise FileNotFoundError(
            f"dbt project가 없습니다:\n"
            f"{DBT_DIR}"
        )

    print(
        "[OK] Project structure"
    )


# =========================================================
# 9. Python Script Execution
# =========================================================

def run_python_script(
    script_path,
):

    run_command(
        [
            sys.executable,
            str(
                script_path
            ),
        ],
        cwd=PROJECT_ROOT,
    )


# =========================================================
# 10. Notebook Execution
# =========================================================

def run_notebook(
    notebook_path,
):

    require_file(
        notebook_path
    )

    run_command(
        [
            sys.executable,
            "-m",
            "jupyter",
            "nbconvert",
            "--to",
            "notebook",
            "--execute",
            "--inplace",
            "--ExecutePreprocessor.timeout=600",
            str(
                notebook_path
            ),
        ],
        cwd=PROJECT_ROOT,
    )


# =========================================================
# 11. dbt
# =========================================================

def run_dbt(
    *args,
):

    run_command(
        [
            "dbt",
            *args,
        ],
        cwd=DBT_DIR,
    )


# =========================================================
# 12. DB Engine
# =========================================================

def get_engine():

    if DB_USER is None:
        raise ValueError(
            "DB_USER 또는 POSTGRES_USER가 없습니다."
        )

    try:
        import psycopg  # noqa: F401

        driver = "postgresql+psycopg"

    except ImportError:

        try:
            import psycopg2  # noqa: F401

            driver = "postgresql+psycopg2"

        except ImportError:

            raise ImportError(
                "PostgreSQL driver가 없습니다.\n"
                "psycopg 또는 psycopg2가 필요합니다."
            )


    database_url = URL.create(
        drivername=driver,
        username=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=int(DB_PORT),
        database=DB_NAME,
    )


    return create_engine(
        database_url,
        pool_pre_ping=True,
    )


# =========================================================
# 13. Final DB Validation
# =========================================================

def validate_final_marts():

    engine = (
        get_engine()
    )

    query = """
    select
        count(*) as row_count,
        count(distinct decision_week) as unique_weeks,
        min(decision_week) as min_week,
        max(decision_week) as max_week

    from dbt.mart_scm_decision_weekly
    """

    duplicate_query = """
    select count(*)
    from (
        select
            decision_week,
            product_id,
            count(*) as cnt

        from dbt.mart_scm_decision_weekly

        group by
            decision_week,
            product_id

        having count(*) > 1
    ) t
    """

    with (
        engine.connect()
        as conn
    ):

        result = (
            conn.execute(
                text(
                    query
                )
            )
            .mappings()
            .one()
        )

        duplicate_count = (
            conn.execute(
                text(
                    duplicate_query
                )
            )
            .scalar_one()
        )

    engine.dispose()

    if (
        result[
            "row_count"
        ]
        <= 0
    ):

        raise ValueError(
            "최종 Decision Mart가 비어 있습니다."
        )

    if (
        duplicate_count
        > 0
    ):

        raise ValueError(
            "최종 Decision Mart에 "
            "중복 Key가 있습니다."
        )

    print()
    print(
        "Decision Mart Validation"
    )

    print(
        "Rows:",
        result[
            "row_count"
        ],
    )

    print(
        "Unique weeks:",
        result[
            "unique_weeks"
        ],
    )

    print(
        "Period:",
        result[
            "min_week"
        ],
        "~",
        result[
            "max_week"
        ],
    )

    print(
        "Duplicate keys:",
        duplicate_count,
    )


# =========================================================
# 14. CLI
# =========================================================

def parse_args():

    parser = (
        argparse.ArgumentParser(
            description=(
                "RetailOps AX "
                "end-to-end pipeline"
            )
        )
    )

    parser.add_argument(
        "--skip-extract",
        action="store_true",
        help=(
            "공공데이터 API 수집을 "
            "건너뜁니다."
        ),
    )

    parser.add_argument(
        "--skip-brief",
        action="store_true",
        help=(
            "Decision Brief 생성을 "
            "건너뜁니다."
        ),
    )

    return (
        parser.parse_args()
    )


# =========================================================
# 15. Main Pipeline
# =========================================================

def main():

    args = (
        parse_args()
    )

    pipeline_start = (
        perf_counter()
    )

    print_header(
        "RetailOps AX — End-to-End Pipeline"
    )

    print(
        "Project root:",
        PROJECT_ROOT,
    )

    print(
        "Database:",
        f"{DB_HOST}:{DB_PORT}/{DB_NAME}",
    )


    # -----------------------------------------------------
    # Validation
    # -----------------------------------------------------

    validate_project_structure()


    total_steps = 8

    current_step = 0


    # =====================================================
    # STEP 1
    # Public Data Extraction
    # =====================================================

    current_step += 1

    print_step(
        current_step,
        total_steps,
        "공공데이터 수집",
    )

    if args.skip_extract:

        print(
            "[SKIP] API extraction"
        )

    else:

        for script in (
            EXTRACT_SCRIPTS
        ):

            print()
            print(
                f"Running: "
                f"{script.name}"
            )

            run_python_script(
                script
            )


    # =====================================================
    # STEP 2
    # Raw Load
    # =====================================================

    current_step += 1

    print_step(
        current_step,
        total_steps,
        "PostgreSQL raw 적재",
    )

    for script in (
        LOAD_SCRIPTS
    ):

        print()
        print(
            f"Running: "
            f"{script.name}"
        )

        run_python_script(
            script
        )


    # =====================================================
    # STEP 3
    # Market / Feature Mart
    # =====================================================

    current_step += 1

    print_step(
        current_step,
        total_steps,
        "dbt Market / Risk Feature Mart",
    )

    run_dbt(
        "build",
        "--select",
        "+mart_scm_risk_weekly",
    )


    # =====================================================
    # STEP 4
    # Price Risk Model
    # =====================================================

    current_step += 1

    print_step(
        current_step,
        total_steps,
        "Price Risk Model",
    )

    run_notebook(
        RISK_MODEL_NOTEBOOK
    )

    require_file(
        PRICE_RISK_OUTPUT
    )

    print(
        "[OK] Price Risk output:",
        PRICE_RISK_OUTPUT,
    )


    # =====================================================
    # STEP 5
    # SCM Decision Engine
    # =====================================================

    current_step += 1

    print_step(
        current_step,
        total_steps,
        "SCM Decision Engine",
    )

    run_notebook(
        DECISION_NOTEBOOK
    )

    require_file(
        DECISION_OUTPUT
    )

    require_file(
        EVALUATION_OUTPUT
    )

    print(
        "[OK] Decision output:",
        DECISION_OUTPUT,
    )

    print(
        "[OK] Evaluation output:",
        EVALUATION_OUTPUT,
    )


    # =====================================================
    # STEP 6
    # Decision Output Load
    # =====================================================

    current_step += 1

    print_step(
        current_step,
        total_steps,
        "Decision Output PostgreSQL 적재",
    )

    run_python_script(
        DECISION_LOADER
    )


    # =====================================================
    # STEP 7
    # Decision Mart
    # =====================================================

    current_step += 1

    print_step(
        current_step,
        total_steps,
        "dbt Decision Mart Build + Test",
    )

    run_dbt(
        "build",
        "--select",
        "+mart_scm_decision_weekly",
        "+mart_scm_decision_evaluation_weekly",
    )


    # =====================================================
    # STEP 8
    # Brief + Final Validation
    # =====================================================

    current_step += 1

    print_step(
        current_step,
        total_steps,
        "SCM Brief / Final Validation",
    )

    validate_final_marts()

    if args.skip_brief:

        print(
            "[SKIP] SCM Brief"
        )

    elif (
        BRIEF_NOTEBOOK.exists()
    ):

        run_notebook(
            BRIEF_NOTEBOOK
        )

    else:

        print(
            "[WARN] "
            "05_scm_decision_brief.ipynb가 없어 "
            "Brief 생성을 건너뜁니다."
        )


    # =====================================================
    # Complete
    # =====================================================

    elapsed = (
        perf_counter()
        - pipeline_start
    )

    print_header(
        "PIPELINE COMPLETED SUCCESSFULLY"
    )

    print(
        f"Elapsed: "
        f"{elapsed:.1f}s"
    )

    print()

    print(
        "Dashboard:"
    )

    print(
        "  streamlit run app/app.py"
    )

    print()


if __name__ == "__main__":
    main()
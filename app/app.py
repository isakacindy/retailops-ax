# app/app.py

from pathlib import Path
from importlib.util import find_spec
import os

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import URL

# =========================================================
# 1. Page Config
# =========================================================

st.set_page_config(
    page_title="RetailOps AX | SCM Decision Center",
    page_icon="📦",
    layout="wide",
)


# =========================================================
# 2. Global Style
#    - Pretendard
#    - KPI Card
#    - Streamlit Material Icon 보호
# =========================================================

st.markdown(
    """
    <style>

    /* -----------------------------------------------------
       Pretendard
    ----------------------------------------------------- */

    @font-face {
        font-family: 'Pretendard';
        src: url('https://cdn.jsdelivr.net/gh/projectnoonnu/pretendard@1.0/Pretendard-Thin.woff2') format('woff2');
        font-weight: 100;
        font-display: swap;
    }

    @font-face {
        font-family: 'Pretendard';
        src: url('https://cdn.jsdelivr.net/gh/projectnoonnu/pretendard@1.0/Pretendard-ExtraLight.woff2') format('woff2');
        font-weight: 200;
        font-display: swap;
    }

    @font-face {
        font-family: 'Pretendard';
        src: url('https://cdn.jsdelivr.net/gh/projectnoonnu/pretendard@1.0/Pretendard-Light.woff2') format('woff2');
        font-weight: 300;
        font-display: swap;
    }

    @font-face {
        font-family: 'Pretendard';
        src: url('https://cdn.jsdelivr.net/gh/projectnoonnu/pretendard@1.0/Pretendard-Regular.woff2') format('woff2');
        font-weight: 400;
        font-display: swap;
    }

    @font-face {
        font-family: 'Pretendard';
        src: url('https://cdn.jsdelivr.net/gh/projectnoonnu/pretendard@1.0/Pretendard-Medium.woff2') format('woff2');
        font-weight: 500;
        font-display: swap;
    }

    @font-face {
        font-family: 'Pretendard';
        src: url('https://cdn.jsdelivr.net/gh/projectnoonnu/pretendard@1.0/Pretendard-SemiBold.woff2') format('woff2');
        font-weight: 600;
        font-display: swap;
    }

    @font-face {
        font-family: 'Pretendard';
        src: url('https://cdn.jsdelivr.net/gh/projectnoonnu/pretendard@1.0/Pretendard-Bold.woff2') format('woff2');
        font-weight: 700;
        font-display: swap;
    }

    @font-face {
        font-family: 'Pretendard';
        src: url('https://cdn.jsdelivr.net/gh/projectnoonnu/pretendard@1.0/Pretendard-ExtraBold.woff2') format('woff2');
        font-weight: 800;
        font-display: swap;
    }

    @font-face {
        font-family: 'Pretendard';
        src: url('https://cdn.jsdelivr.net/gh/projectnoonnu/pretendard@1.0/Pretendard-Black.woff2') format('woff2');
        font-weight: 900;
        font-display: swap;
    }


    /* -----------------------------------------------------
       Pretendard 적용
       
       중요:
       span 전체에 적용하지 않음.
       Streamlit Material Icon의 ligature가 깨지는 것을 방지.
    ----------------------------------------------------- */

    html,
    body,
    [data-testid="stAppViewContainer"],
    [data-testid="stSidebar"],
    .stMarkdown,
    .stCaptionContainer,
    [data-testid="stMetric"],
    [data-testid="stDataFrame"],
    [data-testid="stSelectbox"],
    [data-testid="stTextInput"],
    label,
    input,
    textarea,
    h1,
    h2,
    h3,
    h4,
    h5,
    h6,
    p {
        font-family:
            'Pretendard',
            -apple-system,
            BlinkMacSystemFont,
            'Apple SD Gothic Neo',
            'Noto Sans KR',
            sans-serif !important;
    }


    /* -----------------------------------------------------
       Streamlit Material Icon 보호
    ----------------------------------------------------- */

    [data-testid="stIconMaterial"],
    .material-symbols-rounded,
    .material-symbols-outlined {
        font-family: 'Material Symbols Rounded',
                     'Material Symbols Outlined' !important;
    }


    /* -----------------------------------------------------
       Main Layout
    ----------------------------------------------------- */

    .block-container {
        max-width: 1360px;
        padding-top: 2.2rem;
        padding-bottom: 4rem;
    }

    h1,
    h2,
    h3 {
        letter-spacing: -0.035em;
    }

    h1 {
        font-weight: 750 !important;
    }

    h2,
    h3 {
        font-weight: 700 !important;
    }


    /* -----------------------------------------------------
       Sidebar
    ----------------------------------------------------- */

    section[data-testid="stSidebar"] {
        border-right: 1px solid #ECEFF3;
    }


    /* -----------------------------------------------------
       Custom KPI Cards
    ----------------------------------------------------- */

    .kpi-card {
        height: 168px;

        padding:
            22px
            26px;

        border:
            1px solid
            #E2E5EA;

        border-radius:
            20px;

        background:
            #FFFFFF;

        display:
            flex;

        flex-direction:
            column;

        justify-content:
            space-between;

        box-sizing:
            border-box;
    }


    .kpi-label {
        font-family:
            'Pretendard',
            sans-serif;

        font-size:
            15px;

        font-weight:
            600;

        color:
            #7A8190;

        letter-spacing:
            -0.02em;
    }


    .kpi-value-row {
        display:
            flex;

        align-items:
            center;

        gap:
            10px;

        flex-wrap:
            nowrap;
    }


    .kpi-value {
        font-family:
            'Pretendard',
            sans-serif;

        font-size:
            38px;

        line-height:
            1.08;

        font-weight:
            750;

        letter-spacing:
            -0.04em;

        color:
            #101827;

        white-space:
            nowrap;
    }


    .kpi-delta {
        display:
            inline-flex;

        align-items:
            center;

        justify-content:
            center;

        padding:
            5px
            9px;

        border-radius:
            999px;

        font-family:
            'Pretendard',
            sans-serif;

        font-size:
            13px;

        line-height:
            1;

        font-weight:
            600;

        white-space:
            nowrap;
    }


    .kpi-delta-good {
        color:
            #16803A;

        background:
            #EAF8EE;
    }


    .kpi-delta-bad {
        color:
            #B42318;

        background:
            #FEECEB;
    }


    .kpi-delta-neutral {
        color:
            #747B87;

        background:
            #F0F1F3;
    }


    .kpi-subtitle {
        font-family:
            'Pretendard',
            sans-serif;

        font-size:
            13px;

        line-height:
            1.4;

        font-weight:
            400;

        color:
            #8A909B;

        letter-spacing:
            -0.01em;
    }


    /* -----------------------------------------------------
       기본 Streamlit Metric
       - KPI 카드 외 다른 metric에서 사용
    ----------------------------------------------------- */

    [data-testid="stMetric"] {
        font-family:
            'Pretendard',
            sans-serif;
    }


    /* -----------------------------------------------------
       Alert
    ----------------------------------------------------- */

    .stAlert {
        border-radius:
            12px;
    }


    /* -----------------------------------------------------
       Expander
       
       icon 영역에 Pretendard를 강제하지 않음.
    ----------------------------------------------------- */

    div[data-testid="stExpander"] {
        border:
            1px solid
            #E2E5EA;

        border-radius:
            12px;

        overflow:
            hidden;
    }


    div[data-testid="stExpander"] summary {
        min-height:
            52px;

        align-items:
            center;
    }


    div[data-testid="stExpander"] summary p {
        font-family:
            'Pretendard',
            sans-serif !important;

        font-size:
            15px !important;

        font-weight:
            600 !important;

        margin:
            0 !important;
    }


    /* -----------------------------------------------------
       Dataframe
    ----------------------------------------------------- */

    [data-testid="stDataFrame"] {
        border-radius:
            10px;

        overflow:
            hidden;
    }


    /* -----------------------------------------------------
       Divider
    ----------------------------------------------------- */

    hr {
        margin-top:
            2rem !important;

        margin-bottom:
            2rem !important;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 3. Project / DB Config
# =========================================================

PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[1]
)

load_dotenv(
    PROJECT_ROOT
    / ".env"
)


def get_env(
    *names,
    default=None,
):

    for name in names:

        value = (
            os.getenv(
                name
            )
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
# 4. Database
# =========================================================

def get_postgres_driver():

    if (
        find_spec(
            "psycopg"
        )
        is not None
    ):

        return (
            "postgresql+psycopg"
        )

    if (
        find_spec(
            "psycopg2"
        )
        is not None
    ):

        return (
            "postgresql+psycopg2"
        )

    raise ImportError(
        "psycopg 또는 psycopg2가 필요합니다."
    )


@st.cache_resource
def get_engine():

    driver = (
        get_postgres_driver()
    )

    database_url = (
        URL.create(
            drivername=driver,
            username=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=int(
                DB_PORT
            ),
            database=DB_NAME,
        )
    )

    return (
        create_engine(
            database_url,
            pool_pre_ping=True,
        )
    )


@st.cache_data(
    ttl=300
)
def load_decision_data():

    query = """
    select *
    from dbt.mart_scm_decision_weekly
    order by decision_week
    """

    return (
        pd.read_sql(
            query,
            get_engine(),
            parse_dates=[
                "decision_week"
            ],
        )
    )


@st.cache_data(
    ttl=300
)
def load_evaluation_data():

    query = """
    select *
    from dbt.mart_scm_decision_evaluation_weekly
    order by decision_week
    """

    return (
        pd.read_sql(
            query,
            get_engine(),
            parse_dates=[
                "decision_week"
            ],
        )
    )


# =========================================================
# 5. Display Helper Functions
# =========================================================

def format_kg(
    value,
):

    if pd.isna(
        value
    ):

        return "-"

    return (
        f"{value:,.0f} kg"
    )


def format_index(
    value,
):

    if pd.isna(
        value
    ):

        return "N/A"

    return (
        f"{value:.3f}"
    )


def map_risk_label(
    value,
):

    mapping = {
        "Normal":
            "정상",

        "Watch":
            "주의",

        "Risk":
            "위험",
    }

    if pd.isna(
        value
    ):

        return "N/A"

    return (
        mapping.get(
            str(value),
            str(value),
        )
    )


def map_scope_label(
    value,
):

    mapping = {
        "PUBLIC_ACTUAL":
            "실제 공공데이터",

        "SIMULATED":
            "시뮬레이션",

        "SIMULATION":
            "시뮬레이션",
    }

    if pd.isna(
        value
    ):

        return "-"

    return (
        mapping.get(
            str(value),
            str(value),
        )
    )


def map_quality_label(
    value,
):

    mapping = {
        "OK":
            "정상",

        "NO_PRICE_FORECAST":
            "가격 예측 없음",
    }

    if pd.isna(
        value
    ):

        return "-"

    return (
        mapping.get(
            str(value),
            str(value),
        )
    )


def get_action_title(
    signal,
):

    mapping = {
        "ADVANCE_PURCHASE":
            "선행 발주",

        "EARLY_WATCH_HOLD":
            "주의 상태 유지",

        "OFFSET_REDUCTION":
            "후속 발주량 축소",

        "BASELINE_REPLENISHMENT":
            "기본 보충 발주",

        "BASELINE_NO_FORECAST":
            "예측 없음 · 기본 정책",
    }

    return (
        mapping.get(
            signal,
            signal,
        )
    )


def get_decision_label(
    signal,
):

    return (
        get_action_title(
            signal
        )
    )


# =========================================================
# 6. Custom KPI Renderer
# =========================================================

def render_kpi_card(
    label,
    value,
    subtitle=None,
    delta=None,
    delta_type="neutral",
):

    delta_html = ""

    if delta is not None:
        delta_html = (
            f'<span class="kpi-delta kpi-delta-{delta_type}">'
            f'{delta}'
            f'</span>'
        )

    subtitle_html = ""

    if subtitle:
        subtitle_html = (
            f'<div class="kpi-subtitle">'
            f'{subtitle}'
            f'</div>'
        )

    html = (
        f'<div class="kpi-card">'
        f'<div class="kpi-label">{label}</div>'
        f'<div class="kpi-value-row">'
        f'<div class="kpi-value">{value}</div>'
        f'{delta_html}'
        f'</div>'
        f'{subtitle_html}'
        f'</div>'
    )

    st.html(html)


# =========================================================
# 7. Business Explanation
# =========================================================

def get_risk_explanation(
    row,
):

    current = (
        row[
            "current_risk_level"
        ]
    )

    forecast = (
        row[
            "forecast_risk_level"
        ]
    )


    if not bool(
        row[
            "has_price_forecast"
        ]
    ):

        return (
            "가격 위험 예측값이 없어 "
            "안전재고와 리드타임 기반 "
            "기본 발주 정책을 적용합니다."
        )


    if (
        current == "Normal"
        and forecast == "Watch"
    ):

        return (
            "현재 가격은 정상 범위이나 "
            "다음 주 상대가격 상승 가능성이 감지되었습니다."
        )


    if (
        current == "Normal"
        and forecast == "Risk"
    ):

        return (
            "현재 가격은 정상 범위이나 "
            "다음 주 위험 구간 진입 가능성이 감지되었습니다."
        )


    if (
        current == "Watch"
        and forecast == "Risk"
    ):

        return (
            "가격 위험 수준이 주의에서 위험 단계로 "
            "확대될 가능성이 있습니다."
        )


    if (
        current == "Risk"
        and forecast
        in [
            "Watch",
            "Normal",
        ]
    ):

        return (
            "현재 가격은 위험 수준이지만 "
            "다음 주에는 완화될 가능성이 있습니다. "
            "추가 선행구매보다 기존 확보재고와 "
            "후속 발주 조정이 우선됩니다."
        )


    if current == "Risk":

        return (
            "현재 가격이 이미 위험 수준입니다. "
            "추가 선행구매보다 기존 확보재고와 "
            "후속 발주 조정이 우선됩니다."
        )


    return (
        "현재 뚜렷한 가격 위험 확대 신호는 없습니다."
    )


def get_action_message(
    row,
):

    baseline_qty = (
        row[
            "baseline_order_qty_kg"
        ]
    )

    recommended_qty = (
        row[
            "recommended_order_qty_kg"
        ]
    )

    shift_qty = (
        row[
            "order_timing_shift_kg"
        ]
    )

    signal = (
        row[
            "decision_signal"
        ]
    )


    if signal == "ADVANCE_PURCHASE":

        return (
            f"기본 발주량 {baseline_qty:,.0f}kg 대비 "
            f"{shift_qty:,.0f}kg을 앞당겨 "
            f"총 {recommended_qty:,.0f}kg 발주를 권고합니다."
        )


    if signal == "OFFSET_REDUCTION":

        return (
            "이전 선행발주 물량을 반영하여 "
            f"기본 발주량 대비 {abs(shift_qty):,.0f}kg 축소한 "
            f"{recommended_qty:,.0f}kg 발주를 권고합니다."
        )


    if signal == "EARLY_WATCH_HOLD":

        return (
            "가격 주의 신호가 감지되었으나 "
            "현재 재고 포지션이 충분하여 "
            "추가 선행발주는 권고하지 않습니다."
        )


    if signal == "BASELINE_NO_FORECAST":

        return (
            "가격 예측값이 없어 "
            f"기본 발주 정책 기준 {recommended_qty:,.0f}kg를 "
            "권고합니다."
        )


    return (
        "추가 가격 위험 조정 없이 "
        f"기본 정책 기준 {recommended_qty:,.0f}kg 발주를 "
        "권고합니다."
    )


def get_inventory_message(
    row,
):

    return (
        "이번 주 입고 반영 후 "
        f"재고 포지션은 {row['inventory_position_kg']:,.0f}kg이며, "
        "예상 수요 반영 후 "
        f"커버 가능 일수는 {row['ending_days_of_cover']:.1f}일입니다. "
        f"현재 적용 리드타임은 {row['lead_time_days']:.0f}일입니다."
    )


# =========================================================
# 8. Load Data
# =========================================================

try:

    decision = (
        load_decision_data()
    )

    evaluation = (
        load_evaluation_data()
    )

except Exception as e:

    st.error(
        "PostgreSQL / dbt Mart 데이터를 "
        "불러오지 못했습니다."
    )

    st.exception(
        e
    )

    st.stop()


if decision.empty:

    st.warning(
        "의사결정 Mart에 데이터가 없습니다."
    )

    st.stop()


# =========================================================
# 9. Header
# =========================================================

st.title(
    "RetailOps AX"
)

st.caption(
    "국내 유통 데이터 기반 SCM Planning & Decision Automation"
)

st.write(
    "시장 가격 위험을 감지하고 "
    "수요·재고·리드타임을 결합해 "
    "주간 발주 의사결정을 생성합니다."
)

st.divider()


# =========================================================
# 10. Sidebar
# =========================================================

st.sidebar.header(
    "의사결정 조건"
)


product_options = (
    decision[
        [
            "product_id",
            "product_name",
        ]
    ]
    .drop_duplicates()
)


selected_product_id = (
    st.sidebar.selectbox(
        "상품",
        options=(
            product_options[
                "product_id"
            ]
            .tolist()
        ),
        format_func=lambda x:
            (
                product_options.loc[
                    product_options[
                        "product_id"
                    ] == x,
                    "product_name",
                ]
                .iloc[0]
                + f" ({x})"
            ),
    )
)


product_decision = (
    decision[
        decision[
            "product_id"
        ] == selected_product_id
    ]
    .sort_values(
        "decision_week"
    )
    .reset_index(
        drop=True
    )
)


week_options = (
    product_decision[
        "decision_week"
    ]
    .sort_values(
        ascending=False
    )
    .tolist()
)


selected_week = (
    st.sidebar.selectbox(
        "기준 주차",
        options=week_options,
        format_func=lambda x:
            x.strftime(
                "%Y-%m-%d"
            ),
    )
)


current = (
    product_decision[
        product_decision[
            "decision_week"
        ] == selected_week
    ]
    .iloc[0]
)


st.sidebar.divider()


st.sidebar.caption(
    "시장 데이터"
)

st.sidebar.write(
    map_scope_label(
        current[
            "market_data_scope"
        ]
    )
)


st.sidebar.caption(
    "기업 SCM 데이터"
)

st.sidebar.write(
    map_scope_label(
        current[
            "enterprise_data_scope"
        ]
    )
)


st.sidebar.caption(
    "의사결정 범위"
)

st.sidebar.write(
    map_scope_label(
        current[
            "decision_scope"
        ]
    )
)


st.sidebar.caption(
    "정책 버전"
)

st.sidebar.write(
    current[
        "policy_version"
    ]
)


st.sidebar.caption(
    "데이터 품질"
)

st.sidebar.write(
    map_quality_label(
        current[
            "data_quality_flag"
        ]
    )
)


# =========================================================
# 11. Weekly Decision
# =========================================================

st.subheader(
    f"{selected_week.strftime('%Y-%m-%d')} 주간 의사결정"
)

st.caption(
    f"{current['product_name']} · "
    f"{current['product_id']}"
)


# =========================================================
# 12. KPI Cards
# =========================================================

(
    col1,
    col2,
    col3,
    col4,
) = st.columns(4)


# Forecast Delta

forecast_delta = None
forecast_delta_text = None


if (
    pd.notna(
        current[
            "forecast_price_index"
        ]
    )
    and
    pd.notna(
        current[
            "current_price_index"
        ]
    )
):

    forecast_delta = (
        current[
            "forecast_price_index"
        ]
        -
        current[
            "current_price_index"
        ]
    )


    if forecast_delta > 0:

        forecast_arrow = "↑"

    elif forecast_delta < 0:

        forecast_arrow = "↓"

    else:

        forecast_arrow = "→"


    forecast_delta_text = (
        f"{forecast_arrow} "
        f"{forecast_delta:+.3f}"
    )


# Order Delta

order_delta = (
    current[
        "recommended_order_qty_kg"
    ]
    -
    current[
        "baseline_order_qty_kg"
    ]
)


if order_delta > 0:

    order_arrow = "↑"

elif order_delta < 0:

    order_arrow = "↓"

else:

    order_arrow = "→"


order_delta_text = (
    f"{order_arrow} "
    f"{order_delta:+,.0f} kg"
)


# Current Price

with col1:

    render_kpi_card(
        label="현재 가격지수",
        value=format_index(
            current[
                "current_price_index"
            ]
        ),
        subtitle=(
            "현재 위험 수준 · "
            f"{map_risk_label(current['current_risk_level'])}"
        ),
    )


# Forecast Price

with col2:

    if forecast_delta is None:

        price_delta_type = (
            "neutral"
        )

    elif forecast_delta < 0:

        # 위험 완화
        price_delta_type = (
            "good"
        )

    elif forecast_delta > 0:

        # 위험 확대
        price_delta_type = (
            "bad"
        )

    else:

        price_delta_type = (
            "neutral"
        )


    render_kpi_card(
        label="예측 가격지수",
        value=format_index(
            current[
                "forecast_price_index"
            ]
        ),
        delta=(
            forecast_delta_text
        ),
        delta_type=(
            price_delta_type
        ),
        subtitle=(
            "예측 위험 수준 · "
            f"{map_risk_label(current['forecast_risk_level'])}"
        ),
    )


# Inventory

with col3:

    render_kpi_card(
        label="재고 포지션",
        value=format_kg(
            current[
                "inventory_position_kg"
            ]
        ),
        subtitle=(
            "예상 주간 수요 · "
            f"{format_kg(current['forecast_weekly_demand_kg'])}"
        ),
    )


# Order

with col4:

    render_kpi_card(
        label="권장 발주량",
        value=format_kg(
            current[
                "recommended_order_qty_kg"
            ]
        ),
        delta=(
            order_delta_text
        ),
        delta_type="neutral",
        subtitle=(
            get_action_title(
                current[
                    "decision_signal"
                ]
            )
        ),
    )


st.divider()


# =========================================================
# 13. Recommended Action
# =========================================================

st.subheader(
    "권장 액션"
)


signal = (
    current[
        "decision_signal"
    ]
)


if signal == "ADVANCE_PURCHASE":

    st.warning(
        get_action_title(
            signal
        )
    )


elif signal in [
    "OFFSET_REDUCTION",
    "EARLY_WATCH_HOLD",
]:

    st.info(
        get_action_title(
            signal
        )
    )


elif signal == "BASELINE_NO_FORECAST":

    st.warning(
        get_action_title(
            signal
        )
    )


else:

    st.success(
        get_action_title(
            signal
        )
    )


st.markdown(
    f"### {get_action_message(current)}"
)


(
    action_col1,
    action_col2,
    action_col3,
) = st.columns(3)


with action_col1:

    st.metric(
        "기본 발주량",
        format_kg(
            current[
                "baseline_order_qty_kg"
            ]
        ),
    )


with action_col2:

    st.metric(
        "권장 발주량",
        format_kg(
            current[
                "recommended_order_qty_kg"
            ]
        ),
    )


with action_col3:

    st.metric(
        "발주 조정량",
        format_kg(
            current[
                "order_timing_shift_kg"
            ]
        ),
    )


st.caption(
    current[
        "decision_reason"
    ]
)


# =========================================================
# 14. Market + Inventory
# =========================================================

st.divider()

left, right = (
    st.columns(2)
)


# ---------------------------------------------------------
# Market
# ---------------------------------------------------------

with left:

    st.subheader(
        "시장 가격 위험"
    )

    st.write(
        get_risk_explanation(
            current
        )
    )


    price_history = (
        product_decision[
            product_decision[
                "decision_week"
            ] <= selected_week
        ][
            [
                "decision_week",
                "current_price_index",
                "forecast_price_index",
            ]
        ]
        .tail(20)
        .copy()
    )


    price_long = (
        price_history
        .melt(
            id_vars=[
                "decision_week"
            ],
            value_vars=[
                "current_price_index",
                "forecast_price_index",
            ],
            var_name="series",
            value_name="price_index",
        )
    )


    price_long[
        "series"
    ] = (
        price_long[
            "series"
        ]
        .map({
            "current_price_index":
                "현재",

            "forecast_price_index":
                "예측",
        })
    )


    price_chart = (
        alt.Chart(
            price_long
        )
        .mark_line(
            point=True
        )
        .encode(
            x=alt.X(
                "decision_week:T",
                title="주차",
            ),

            y=alt.Y(
                "price_index:Q",
                title="상대가격지수",
                scale=alt.Scale(
                    zero=False
                ),
            ),

            strokeDash=alt.StrokeDash(
                "series:N",
                title=None,
            ),

            tooltip=[
                alt.Tooltip(
                    "decision_week:T",
                    title="주차",
                    format="%Y-%m-%d",
                ),

                alt.Tooltip(
                    "series:N",
                    title="구분",
                ),

                alt.Tooltip(
                    "price_index:Q",
                    title="가격지수",
                    format=".3f",
                ),
            ],
        )
    )


    threshold_df = (
        pd.DataFrame({
            "threshold": [
                1.05,
                1.15,
            ],

            "label": [
                "주의 기준",
                "위험 기준",
            ],
        })
    )


    threshold_chart = (
        alt.Chart(
            threshold_df
        )
        .mark_rule(
            strokeDash=[
                5,
                5,
            ]
        )
        .encode(
            y=alt.Y(
                "threshold:Q",
            ),

            tooltip=[
                alt.Tooltip(
                    "label:N",
                    title="기준",
                ),

                alt.Tooltip(
                    "threshold:Q",
                    title="가격지수",
                    format=".2f",
                ),
            ],
        )
    )


    st.altair_chart(
        price_chart
        + threshold_chart,
        use_container_width=True,
    )


# ---------------------------------------------------------
# Inventory
# ---------------------------------------------------------

with right:

    st.subheader(
        "재고 상태"
    )

    st.write(
        get_inventory_message(
            current
        )
    )


    inventory_metrics = (
        pd.DataFrame({
            "metric": [
                "가용 재고",
                "미입고 발주량",
                "예상 주간 수요",
            ],

            "quantity_kg": [
                current[
                    "beginning_inventory_kg"
                ],

                current[
                    "open_order_qty_kg"
                ],

                current[
                    "forecast_weekly_demand_kg"
                ],
            ],
        })
    )


    inventory_chart = (
        alt.Chart(
            inventory_metrics
        )
        .mark_bar()
        .encode(
            x=alt.X(
                "quantity_kg:Q",
                title="수량 (kg)",
            ),

            y=alt.Y(
                "metric:N",
                title=None,
                sort=None,
            ),

            tooltip=[
                alt.Tooltip(
                    "metric:N",
                    title="항목",
                ),

                alt.Tooltip(
                    "quantity_kg:Q",
                    title="수량",
                    format=",.0f",
                ),
            ],
        )
    )


    st.altair_chart(
        inventory_chart,
        use_container_width=True,
    )


    (
        inv_col1,
        inv_col2,
        inv_col3,
        inv_col4,
    ) = st.columns(4)


    with inv_col1:

        st.metric(
            "이번 주 입고량",
            format_kg(
                current[
                    "inbound_qty_kg"
                ]
            ),
        )


    with inv_col2:

        st.metric(
            "재고 커버일수",
            f"{current['ending_days_of_cover']:.1f}일",
        )


    with inv_col3:

        st.metric(
            "리드타임",
            f"{current['lead_time_days']:.0f}일",
        )


    with inv_col4:

        st.metric(
            "안전재고",
            f"{current['safety_stock_days']:.0f}일",
        )


# =========================================================
# 15. History
# =========================================================

st.divider()

st.subheader(
    "주간 의사결정 이력"
)


history = (
    product_decision[
        product_decision[
            "decision_week"
        ] <= selected_week
    ]
    .sort_values(
        "decision_week",
        ascending=False,
    )
    .copy()
)


history_display = (
    history[
        [
            "decision_week",
            "current_risk_level",
            "forecast_risk_level",
            "baseline_order_qty_kg",
            "recommended_order_qty_kg",
            "order_timing_shift_kg",
            "decision_signal",
            "data_quality_flag",
        ]
    ]
    .copy()
)


history_display[
    "decision_week"
] = (
    history_display[
        "decision_week"
    ]
    .dt.strftime(
        "%Y-%m-%d"
    )
)


history_display[
    "current_risk_level"
] = (
    history_display[
        "current_risk_level"
    ]
    .apply(
        map_risk_label
    )
)


history_display[
    "forecast_risk_level"
] = (
    history_display[
        "forecast_risk_level"
    ]
    .apply(
        map_risk_label
    )
)


history_display[
    "decision_signal"
] = (
    history_display[
        "decision_signal"
    ]
    .map(
        get_decision_label
    )
)


history_display[
    "data_quality_flag"
] = (
    history_display[
        "data_quality_flag"
    ]
    .apply(
        map_quality_label
    )
)


history_display = (
    history_display.rename(
        columns={
            "decision_week":
                "주차",

            "current_risk_level":
                "현재 위험",

            "forecast_risk_level":
                "예측 위험",

            "baseline_order_qty_kg":
                "기본 발주량",

            "recommended_order_qty_kg":
                "권장 발주량",

            "order_timing_shift_kg":
                "발주 조정량",

            "decision_signal":
                "의사결정",

            "data_quality_flag":
                "데이터 품질",
        }
    )
)


st.dataframe(
    history_display,
    use_container_width=True,
    hide_index=True,
    height=430,
    column_config={
        "기본 발주량":
            st.column_config.NumberColumn(
                format="%.0f kg",
            ),

        "권장 발주량":
            st.column_config.NumberColumn(
                format="%.0f kg",
            ),

        "발주 조정량":
            st.column_config.NumberColumn(
                format="%+.0f kg",
            ),
    },
)


# =========================================================
# 16. Policy Backtest
# =========================================================

st.divider()

st.subheader(
    "정책 백테스트"
)

st.caption(
    "전체 백테스트 기간을 기준으로 "
    "가격 위험 정책의 동작 결과를 요약합니다."
)


product_eval = (
    evaluation[
        evaluation[
            "product_id"
        ] == selected_product_id
    ]
    .copy()
)


advance_eval = (
    product_eval[
        product_eval[
            "decision_signal"
        ] == "ADVANCE_PURCHASE"
    ]
    .copy()
)


trigger_count = (
    len(
        advance_eval
    )
)


actual_increase_count = (
    advance_eval[
        "actual_price_increase"
    ]
    .fillna(
        False
    )
    .astype(
        bool
    )
    .sum()
)


total_advance_order = (
    product_decision.loc[
        product_decision[
            "order_timing_shift_kg"
        ] > 0,
        "order_timing_shift_kg",
    ]
    .sum()
)


total_offset_reduction = (
    -product_decision.loc[
        product_decision[
            "order_timing_shift_kg"
        ] < 0,
        "order_timing_shift_kg",
    ]
    .sum()
)


net_order_change = (
    product_decision[
        "recommended_order_qty_kg"
    ].sum()
    -
    product_decision[
        "baseline_order_qty_kg"
    ].sum()
)


timing_offset_ratio = (
    total_offset_reduction
    / total_advance_order
    * 100

    if total_advance_order > 0

    else np.nan
)


(
    eval_col1,
    eval_col2,
    eval_col3,
    eval_col4,
) = st.columns(4)


with eval_col1:

    st.metric(
        "선행 발주 트리거",
        f"{trigger_count}건",
    )


with eval_col2:

    trigger_result = (
        f"{int(actual_increase_count)} / {trigger_count}"
        if trigger_count > 0
        else "-"
    )

    st.metric(
        "실제 다음 주 지수 상승",
        trigger_result,
    )


with eval_col3:

    st.metric(
        "선행 발주 총량",
        format_kg(
            total_advance_order
        ),
    )


with eval_col4:

    st.metric(
        "순발주 증감",
        format_kg(
            net_order_change
        ),
    )


if pd.notna(
    timing_offset_ratio
):

    st.caption(
        f"선행 발주 {trigger_count}건 중 "
        f"{int(actual_increase_count)}건에서 "
        "실제 다음 주 상대가격지수 상승이 관찰되었습니다. "
        f"전체 기간에는 {total_advance_order:,.0f}kg을 선행 발주하고 "
        f"이후 {total_offset_reduction:,.0f}kg을 후속 발주에서 감축하여 "
        f"타이밍 상쇄율은 {timing_offset_ratio:.1f}%였습니다. "
        "다만 표본 수가 제한적이므로 "
        "일반화된 예측 정확도로 해석하지 않습니다."
    )


else:

    st.caption(
        "선행 발주 사례가 없어 "
        "타이밍 상쇄율을 계산하지 않았습니다."
    )


# =========================================================
# 17. Data Scope & Methodology
# =========================================================

st.divider()


with st.expander(
    "데이터 범위 및 방법론",
    expanded=False,
):

    st.markdown(
        """
### 데이터 범위

| 구분 | 데이터 | 범위 |
|---|---|---|
| 시장가격 | 국내 공공데이터 | 실제 관측 |
| 가격 위험 모델 | 시장가격 피처 | 시계열 검증 |
| 수요 | 기업 내부 데이터 대체 | 시뮬레이션 |
| 재고 | 기업 내부 데이터 대체 | 시뮬레이션 |
| 입고량 | 기업 내부 데이터 대체 | 시뮬레이션 |
| 리드타임 | 기업 내부 데이터 대체 | 시뮬레이션 |
| 안전재고 | 정책 변수 | 시뮬레이션 |
| 권장 발주량 | SCM 의사결정 엔진 | 시뮬레이션 |

### 재고 정책

리드타임, 예상 수요, 안전재고를 이용해
재고 안정성과 서비스 수준을 관리합니다.

### 가격 위험 정책

시장 가격 위험 예측을 이용해
가격 상승 가능성이 사전에 감지되는 경우
일부 발주 시점을 앞당깁니다.

선행 확보된 물량은 이후 주차의 재고 포지션에 반영하고,
필요한 경우 후속 발주량을 축소합니다.

### 해석 시 유의사항

시장 가격은 실제 국내 공공데이터를 사용했습니다.

반면 기업 내부 POS, 실제 재고, 실제 입고량,
실제 리드타임 데이터는 사용하지 않았습니다.

따라서 수요·재고·리드타임 및 권장 발주량은
의사결정 로직 검증을 위한 시뮬레이션 결과입니다.

또한 선행 발주 사례가 4건으로 제한적이므로,
백테스트에서 관찰된 가격 상승 결과를
일반화된 예측 정확도로 해석하지 않습니다.
"""
    )


# =========================================================
# 18. Footer
# =========================================================

st.divider()

st.caption(
    "RetailOps AX · SCM Planning & Decision Automation"
)
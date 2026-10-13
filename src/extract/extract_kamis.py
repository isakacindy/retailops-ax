import os
import math
from pathlib import Path
from urllib.parse import unquote

import pandas as pd
import requests
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

BASE_URL = "https://apis.data.go.kr/B552845/perDay/price"

SERVICE_KEY = unquote(
    os.getenv("DATA_GO_KR_API_KEY")
)

ROWS_PER_PAGE = 1000

START_DATE = "20231016"
END_DATE = "20261010"


def fetch_page(page_no: int):
    params = {
        "serviceKey": SERVICE_KEY,
        "returnType": "JSON",
        "pageNo": page_no,
        "numOfRows": ROWS_PER_PAGE,

        "cond[exmn_ymd::GTE]": START_DATE,
        "cond[exmn_ymd::LTE]": END_DATE,

        "cond[ctgry_cd::EQ]": "200",   # 채소류
        "cond[item_cd::EQ]": "245",    # 양파
        "cond[se_cd::EQ]": "01",       # 소매
        "cond[sgg_cd::EQ]": "1101",    # 서울
    }

    response = requests.get(
        BASE_URL,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    body = response.json()["response"]["body"]

    items = body.get("items", {}).get("item", [])

    if isinstance(items, dict):
        items = [items]

    return body, items


def fetch_all():
    first_body, first_items = fetch_page(1)

    total_count = int(first_body["totalCount"])
    total_pages = math.ceil(
        total_count / ROWS_PER_PAGE
    )

    print(f"전체 건수: {total_count:,}")
    print(f"전체 페이지: {total_pages}")

    all_items = first_items

    for page in range(2, total_pages + 1):
        _, items = fetch_page(page)

        all_items.extend(items)

        print(
            f"[{page}/{total_pages}] "
            f"누적 {len(all_items):,}건"
        )

    return all_items


def transform(items):
    df = pd.DataFrame(items)

    df["exmn_ymd"] = pd.to_datetime(
        df["exmn_ymd"],
        format="%Y%m%d"
    )

    numeric_cols = [
        "exmn_dd_prc",
        "exmn_dd_cnvs_prc",
        "unit_sz",
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

    return df


def print_summary(df):
    print("\n===== DATA SUMMARY =====")

    print("행 수:", len(df))

    print(
        "기간:",
        df["exmn_ymd"].min().date(),
        "~",
        df["exmn_ymd"].max().date()
    )

    print("\n품종:")
    print(
        df[
            ["vrty_cd", "vrty_nm"]
        ]
        .drop_duplicates()
        .sort_values("vrty_cd")
        .to_string(index=False)
    )

    print("\n등급:")
    print(
        df[
            ["grd_cd", "grd_nm"]
        ]
        .drop_duplicates()
        .to_string(index=False)
    )

    print("\n시장 수:")
    print(df["mrkt_cd"].nunique())

    print("\n결측치:")
    print(df.isna().sum())


def grain_check(df):
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

    result = (
        df.groupby(grain_cols, dropna=False)
        .size()
        .reset_index(name="count")
    )

    duplicates = result[
        result["count"] > 1
    ]

    print("\n===== GRAIN CHECK =====")

    print(
        "예상 Grain 중복 조합:",
        len(duplicates)
    )

    if not duplicates.empty:
        print(
            duplicates
            .sort_values(
                "count",
                ascending=False
            )
            .head(20)
            .to_string(index=False)
        )


def save_raw(df):
    output_dir = (
        PROJECT_ROOT /
        "data" /
        "raw"
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    path = (
        output_dir /
        "kamis_onion_seoul_raw.csv"
    )

    df.to_csv(
        path,
        index=False,
        encoding="utf-8-sig"
    )

    print(f"\n저장 완료: {path}")


if __name__ == "__main__":

    items = fetch_all()

    df = transform(items)

    print_summary(df)

    grain_check(df)

    save_raw(df)
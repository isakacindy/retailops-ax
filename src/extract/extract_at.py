
import os
import math
import requests
import pandas as pd

from dotenv import load_dotenv
from urllib.parse import unquote
from pathlib import Path


load_dotenv()

BASE_URL = "https://apis.data.go.kr/B552845/katOnline/trades"
SERVICE_KEY = unquote(os.getenv("DATA_GO_KR_API_KEY"))

PRODUCT_CODE = "1201"   # 양파
ROWS_PER_PAGE = 100


def fetch_page(page_no: int):
    params = {
        "serviceKey": SERVICE_KEY,
        "returnType": "JSON",
        "pageNo": page_no,
        "numOfRows": ROWS_PER_PAGE,
        "cond[onln_whsl_mrkt_mclsf_cd::EQ]": PRODUCT_CODE,
    }

    response = requests.get(BASE_URL, params=params, timeout=30)
    response.raise_for_status()

    body = response.json()["response"]["body"]

    items = body.get("items", {}).get("item", [])

    if isinstance(items, dict):
        items = [items]

    return body, items


def fetch_all():
    first_body, first_items = fetch_page(1)

    total_count = int(first_body["totalCount"])
    total_pages = math.ceil(total_count / ROWS_PER_PAGE)

    print(f"전체 건수: {total_count}")
    print(f"전체 페이지: {total_pages}")

    all_items = first_items

    for page in range(2, total_pages + 1):
        _, items = fetch_page(page)
        all_items.extend(items)

        print(
            f"[{page}/{total_pages}] "
            f"누적 {len(all_items)}건"
        )

    return all_items


def transform(items):
    df = pd.DataFrame(items)

    # 날짜
    df["cfmtn_ymd"] = pd.to_datetime(df["cfmtn_ymd"])

    # 숫자형
    numeric_cols = [
        "cfmtn_qty",
        "avgprc",
        "lwprc",
        "hgprc",
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def save_raw(df):
    output_dir = Path("data/raw")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / "at_onion_raw.csv"

    df.to_csv(
        output_path,
        index=False,
        encoding="utf-8-sig"
    )

    print(f"\n저장 완료: {output_path}")


def print_summary(df):
    print("\n===== DATA SUMMARY =====")

    print("행 수:", len(df))

    print(
        "기간:",
        df["cfmtn_ymd"].min().date(),
        "~",
        df["cfmtn_ymd"].max().date()
    )

    print("\n소분류:")
    print(
        df[
            [
                "onln_whsl_mrkt_sclsf_cd",
                "onln_whsl_mrkt_sclsf_nm"
            ]
        ]
        .drop_duplicates()
        .sort_values("onln_whsl_mrkt_sclsf_cd")
        .to_string(index=False)
    )

    print("\n결측치:")
    print(df.isna().sum())

    print("\n중복 행:")
    print(df.duplicated().sum())


if __name__ == "__main__":
    items = fetch_all()

    df = transform(items)

    print_summary(df)

    save_raw(df)

# 같은 날짜 + 같은 소분류 코드가 여러 건인지 확인
grain_check = (
    df.groupby(
        ["cfmtn_ymd", "onln_whsl_mrkt_sclsf_cd"]
    )
    .size()
    .reset_index(name="count")
)

duplicates_by_grain = grain_check[
    grain_check["count"] > 1
]

print("\n===== GRAIN CHECK =====")
print(
    "동일 날짜 + 동일 소분류 코드 중복 조합:",
    len(duplicates_by_grain)
)

if not duplicates_by_grain.empty:
    print(
        duplicates_by_grain
        .sort_values("count", ascending=False)
        .head(20)
        .to_string(index=False)
    )


# 코드 하나에 명칭이 여러 개 붙는 경우
name_check = (
    df.groupby("onln_whsl_mrkt_sclsf_cd")
      ["onln_whsl_mrkt_sclsf_nm"]
      .nunique()
)

print("\n===== MASTER DATA CHECK =====")
print(
    name_check[name_check > 1]
)

for code in name_check[name_check > 1].index:
    print(
        code,
        df.loc[
            df["onln_whsl_mrkt_sclsf_cd"] == code,
            "onln_whsl_mrkt_sclsf_nm"
        ].unique()
    )
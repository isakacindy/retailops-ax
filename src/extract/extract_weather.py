import os
from pathlib import Path
from urllib.parse import unquote

import pandas as pd
import requests
from dotenv import load_dotenv


# 환경변수
load_dotenv()

SERVICE_KEY = unquote(
    os.getenv("DATA_GO_KR_API_KEY", "")
)

if not SERVICE_KEY:
    raise ValueError(
        "DATA_GO_KR_API_KEY가 .env에 설정되어 있지 않습니다."
    )


# API 설정
BASE_URL = (
    "https://apis.data.go.kr/"
    "1360000/AsosDalyInfoService/"
    "getWthrDataList"
)

# 현재 분석기간보다 앞에서 시작
# → 향후 rolling weather feature 계산 시
#   초기 구간 데이터 부족을 줄이기 위함
START_DATE = "20230101"
END_DATE = "20261010"

PAGE_SIZE = 999


# 양파 생산권 대표 ASOS 지점
STATIONS = {
    "165": "MOKPO", # 서남전남(무안·신안·함평) 기상 proxy
    "285": "HAPCHEON", # 경남(합천·창녕·함양) 기상 proxy
    "184": "JEJU", # 조생종 생산권 보완
}

# API 호출
def fetch_station(station_id: str):

    all_rows = []

    page = 1

    while True:

        params = {
            "serviceKey": SERVICE_KEY,
            "pageNo": page,
            "numOfRows": PAGE_SIZE,
            "dataType": "JSON",
            "dataCd": "ASOS",
            "dateCd": "DAY",
            "startDt": START_DATE,
            "endDt": END_DATE,
            "stnIds": station_id,
        }

        response = requests.get(
            BASE_URL,
            params=params,
            timeout=30
        )

        response.raise_for_status()

        data = response.json()

        # API 자체 오류 확인
        header = (
            data
            .get("response", {})
            .get("header", {})
        )

        result_code = str(
            header.get("resultCode", "")
        )

        if result_code not in ("00", "0"):

            raise RuntimeError(
                f"API 오류 "
                f"station={station_id} "
                f"code={result_code} "
                f"message={header.get('resultMsg')}"
            )


        body = (
            data
            .get("response", {})
            .get("body", {})
        )

        total_count = int(
            body.get("totalCount", 0) or 0
        )

        items_container = body.get("items")

        if not items_container:
            break

        if isinstance(items_container, dict):
            items = items_container.get("item", [])
        else:
            items = []

        if isinstance(items, dict):
            items = [items]

        if not items:
            break

        all_rows.extend(items)

        print(
            f"station={station_id} "
            f"page={page} "
            f"rows={len(items)} "
            f"total={total_count}"
        )

        if page * PAGE_SIZE >= total_count:
            break

        page += 1

    return all_rows


# 전체 지점 수집
rows = []

for station_id, region_code in STATIONS.items():

    station_rows = fetch_station(station_id)

    for row in station_rows:

        # 프로젝트에서 사용하는 생산권 구분값
        row["region_code"] = region_code

    rows.extend(station_rows)


df = pd.DataFrame(rows)


# 필요한 컬럼만 선택
columns = [
    "tm",
    "stnId",
    "stnNm",
    "region_code",

    "avgTa",
    "minTa",
    "maxTa",

    "sumRn",

    "avgRhm",

    "sumSsHr",
    "sumGsr",

    "avgWs",
]

for column in columns:

    if column not in df.columns:
        df[column] = None


df = df[columns].copy()


# 컬럼명 표준화
df = df.rename(
    columns={
        "tm": "weather_date",
        "stnId": "station_id",
        "stnNm": "station_name",

        "avgTa": "avg_temp_c",
        "minTa": "min_temp_c",
        "maxTa": "max_temp_c",

        "sumRn": "precipitation_mm",

        "avgRhm": "avg_humidity_pct",

        "sumSsHr": "sunshine_hours",
        "sumGsr": "solar_radiation_mj_m2",

        "avgWs": "avg_wind_speed_m_s",
    }
)


# 타입 변환
df["weather_date"] = pd.to_datetime(
    df["weather_date"],
    errors="coerce"
)


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


# 중복 제거
df = (
    df
    .drop_duplicates(
        subset=[
            "weather_date",
            "station_id"
        ]
    )
    .sort_values(
        [
            "weather_date",
            "station_id"
        ]
    )
    .reset_index(drop=True)
)


# 저장
output_path = Path(
    "data/raw/kma_asos_onion_regions_raw.csv"
)

output_path.parent.mkdir(
    parents=True,
    exist_ok=True
)

df.to_csv(
    output_path,
    index=False,
    encoding="utf-8-sig"
)

# 검증 출력
print()
print("===== WEATHER EXTRACTION COMPLETE =====")
print(f"rows: {len(df):,}")
print(
    f"period: "
    f"{df['weather_date'].min()} "
    f"~ "
    f"{df['weather_date'].max()}"
)
print()

print(
    df.groupby(
        [
            "station_id",
            "station_name",
            "region_code"
        ]
    ).agg(
        rows=("weather_date", "count"),
        min_date=("weather_date", "min"),
        max_date=("weather_date", "max"),
    )
)

print()
print("NULL RATE")

print(
    (
        df.isna().mean() * 100
    )
    .round(2)
    .sort_values(
        ascending=False
    )
)
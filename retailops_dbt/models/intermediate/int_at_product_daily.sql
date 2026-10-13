with at_source as (

    select *
    from {{ ref('int_at_trade_validated') }}

),

mapping as (

    select *
    from {{ ref('product_source_mapping') }}
    where source = 'AT'

),

mapped as (

    select
        a.trade_date as date,

        m.standard_product_id as product_id,
        m.standard_product_name as product_name,

        a.category_s_cd,
        a.category_s_name,

        a.confirmed_qty,
        a.avg_price,

        a.dq_status,
        a.dq_reason

    from at_source a

    inner join mapping m
        on a.category_m_cd = m.source_product_code

),

daily as (

    select
        date,
        product_id,
        product_name,

        /* -------------------------------------------------
           1. 원천 기준 전체 거래량
           HARD / REVIEW 포함
        ------------------------------------------------- */
        sum(confirmed_qty) as wholesale_qty_raw,


        /* -------------------------------------------------
           2. 분석용 거래량
           HARD_ANOMALY만 제외
           REVIEW는 거래량 자체가 잘못됐다고 확정할 수 없으므로 유지
        ------------------------------------------------- */
        sum(
            case
                when dq_status <> 'HARD_ANOMALY'
                then confirmed_qty
                else 0
            end
        ) as wholesale_qty_clean,


        /* -------------------------------------------------
           3. 가격 계산 대상 거래량
           - 깐양파(120104), 자주양파(120106) 제외
           - HARD_ANOMALY 제외
           - REVIEW는 포함

           기존 가격지표의 denominator
        ------------------------------------------------- */
        sum(
            case
                when category_s_cd not in ('120104', '120106')
                 and dq_status <> 'HARD_ANOMALY'
                then confirmed_qty
                else 0
            end
        ) as wholesale_qty_reference,


        /* -------------------------------------------------
           4. 기본 가중평균 도매가격
           HARD_ANOMALY만 제외
           REVIEW는 포함

           sensitivity 비교용으로 유지
        ------------------------------------------------- */
        sum(
            case
                when category_s_cd not in ('120104', '120106')
                 and dq_status <> 'HARD_ANOMALY'
                then avg_price * confirmed_qty
                else 0
            end
        )
        /
        nullif(
            sum(
                case
                    when category_s_cd not in ('120104', '120106')
                     and dq_status <> 'HARD_ANOMALY'
                    then confirmed_qty
                    else 0
                end
            ),
            0
        ) as wholesale_price_weighted,


        /* -------------------------------------------------
           5. 보수적 가중평균 도매가격
           OK 데이터만 사용

           즉:
           - HARD_ANOMALY 제외
           - REVIEW 제외
           - 깐양파 / 자주양파 제외

           이후 기본 EDA에서는 이 값을 우선 사용
        ------------------------------------------------- */
        sum(
            case
                when category_s_cd not in ('120104', '120106')
                 and dq_status = 'OK'
                then avg_price * confirmed_qty
                else 0
            end
        )
        /
        nullif(
            sum(
                case
                    when category_s_cd not in ('120104', '120106')
                     and dq_status = 'OK'
                    then confirmed_qty
                    else 0
                end
            ),
            0
        ) as wholesale_price_weighted_strict,


        /* -------------------------------------------------
           6. 하루에 거래된 세부 양파 품종 수
        ------------------------------------------------- */
        count(distinct category_s_cd)
            as wholesale_variant_count,


        /* -------------------------------------------------
           7. HARD anomaly 레코드 수
        ------------------------------------------------- */
        count(*) filter (
            where dq_status = 'HARD_ANOMALY'
        ) as hard_anomaly_count,


        /* -------------------------------------------------
           8. REVIEW 레코드 수
        ------------------------------------------------- */
        count(*) filter (
            where dq_status = 'REVIEW'
        ) as review_count,


        /* -------------------------------------------------
           9. REVIEW 거래량 비중

           분모:
           HARD_ANOMALY를 제외한 clean 거래량

           예:
           90%라면 그날 거래량 대부분이
           REVIEW 레코드라는 의미
        ------------------------------------------------- */
        100.0
        * sum(
            case
                when dq_status = 'REVIEW'
                then confirmed_qty
                else 0
            end
        )
        /
        nullif(
            sum(
                case
                    when dq_status <> 'HARD_ANOMALY'
                    then confirmed_qty
                    else 0
                end
            ),
            0
        ) as review_qty_share_pct,


        /* -------------------------------------------------
           10. 해당 날짜에 HARD anomaly가 존재하는지
        ------------------------------------------------- */
        bool_or(
            dq_status = 'HARD_ANOMALY'
        ) as has_hard_anomaly

    from mapped

    group by
        date,
        product_id,
        product_name

)

select *
from daily
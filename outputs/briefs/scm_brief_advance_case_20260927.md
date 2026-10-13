# SCM Weekly Decision Brief

### 기준 주차
2026-09-27

### 상품
양파 (P001)

---

## 1. Market Risk

- Current Price Index: 1.040
- Forecast Price Index: 1.102
- Current Risk: Normal
- Forecast Risk: Watch

현재 가격은 정상 범위이나 다음 주 Watch 수준 상승 가능성이 감지되었습니다.

---

## 2. Inventory Status

- Available Inventory (after receipt): 9,979 kg
- Received This Week: 4,500 kg
- Open Orders: 0 kg
- Inventory Position: 9,979 kg
- Forecast Weekly Demand: 4,928 kg
- Lead Time: 7 days
- Safety Stock Policy: 7 days

이번 주 입고 반영 후 Inventory Position은 9,979kg이며, 발주·수요 반영 후 예상 Days of Cover는 6.8일입니다. 현재 적용 Lead Time은 7일입니다.

---

## 3. Recommended Action

**ADVANCE_PURCHASE**

- Baseline Order: 5,000 kg
- Recommended Order: 6,500 kg
- Timing Adjustment: +1,500 kg
- Price Risk Buffer: 2 days

Baseline 5,000kg 대비 1,500kg을 선행하여 총 6,500kg 발주를 권고합니다.

---

## 4. Decision Reason

Normal→Watch 가격 Risk 선행신호; 2일분 재고 Buffer 반영

---

### Data Scope

- Market Data: PUBLIC_ACTUAL
- Enterprise SCM Data: SIMULATED
- Decision Scope: SIMULATION
- Policy Version: price_early_watch_v1
- Data Quality: OK
# Feature Specification - Recommendation Engine Restore

본 문서는 AlphaPick 추천 포트폴리오를 현재 프로젝트 정책에 맞게 고도화하기 위한 기능 명세서입니다.

핵심 방향은 단순 점수 상위 종목 나열이 아니라, **성향별 편입 허들**, **시장 상황 기반 현금 비중**, **Sector Cap**, **분산 불가 비중의 현금 전환**을 함께 적용하는 포트폴리오 추천입니다.

---

## 1. 적용 원칙

- `MIN_COMPONENT_SCORE = 60` 완화 정책은 사용하지 않습니다.
- 별도 CAN SLIM 화면 복구는 하지 않습니다. CAN SLIM은 점수 산식의 개념적 참고일 뿐, UI 핵심 섹션은 점수 카드/기술 지표/재무 지표/뉴스입니다.
- `total_score`는 리스크가 반영된 참고 점수입니다. 포트폴리오 편입은 회사 가치, 진입 타이밍, 신뢰도 허들을 기준으로 판단합니다.

---

## 2. 성향별 편입 허들

| 투자 성향 | 회사 가치 | 진입 타이밍 | 신뢰도 | 섹터 최대 비중 |
|---|---:|---:|---:|---:|
| 공격형 | 65 | 75 | 65 | 35% |
| 중립형 | 70 | 70 | 70 | 30% |
| 안정형 | 75 | 65 | 75 | 25% |

공격형은 타이밍과 모멘텀을 더 강하게 보고, 안정형은 회사 가치와 데이터 신뢰도를 더 강하게 봅니다.

---

## 3. 현금 비중 추천

현금 비중은 두 기준을 함께 본 뒤 더 보수적인 값을 채택합니다.

### 3.1 편입 후보 수 기준

| 편입 후보 수 | 시장 해석 | 공격형 | 중립형 | 안정형 |
|---:|---|---:|---:|---:|
| 5개 이상 | 강세장 | 0% | 0% | 5% |
| 3~4개 | 중립장 | 10% | 15% | 20% |
| 1~2개 | 약세장 | 20% | 30% | 35% |
| 0개 | 위기장 | 100% | 100% | 100% |

### 3.2 시장 방향 점수 기준

| marketDirection 평균 | 시장 해석 | 공격형 | 중립형 | 안정형 |
|---:|---|---:|---:|---:|
| 65점 이상 | 강세장 | 0% | 0% | 5% |
| 50~64점 | 중립장 | 10% | 15% | 20% |
| 40~49점 | 약세장 | 20% | 30% | 40% |
| 40점 미만 | 위기장 | 35% | 50% | 60% |

예를 들어 편입 후보가 8개라 후보 수 기준 현금이 낮아도, marketDirection 평균이 38점이면 공격형 35%, 중립형 50%, 안정형 60%로 현금 비중이 달라집니다.

---

## 4. Sector Cap 및 재분배

1. 기본 현금을 먼저 제외합니다.
2. 남은 주식 비중을 성향별 균형 점수(`eligibility_score`)의 70점 초과 강도에 비례해 1차 배분합니다.
3. 단일 섹터 비중이 성향별 Sector Cap을 넘으면 초과분을 잘라냅니다.
4. 초과분은 Cap에 여유가 있는 다른 섹터에 점수 비례로 재분배합니다.
5. 재분배할 수 없는 초과분은 현금으로 전환합니다.

이 정책은 섹터 Cap을 무력화하지 않으면서도, 좋은 종목이 특정 섹터에만 몰리는 시장을 보수적으로 처리합니다.

---

## 5. API 응답 필드

`GET /api/portfolio/today/?risk_type=neutral`

```ts
Portfolio {
  baseDate: string
  portfolioScore: number
  eligibilityScore: number
  userRiskType: "aggressive" | "neutral" | "stable"
  riskTypeLabel: string
  hurdles: {
    company: number
    timing: number
    reliability: number
  }
  sectorCap: number
  cashWeight: number
  baseCashWeight: number
  sectorCashWeight: number
  cashReasons: string[]
  marketDirectionScore: number | null
  marketRegime: string
  allocationItems: AllocationItem[]
  items: PortfolioItem[]
}

AllocationItem {
  type: "stock" | "cash"
  ticker: string
  name: string
  sector: string
  weight: number
}
```

---

## 6. 구현 위치

- 백엔드 추천 엔진: `backend/stocks/services.py`
- 오늘의 포트폴리오 API: `backend/stocks/views.py`
- 메인 포트폴리오 화면: `frontend/src/views/HomeView.vue`
- 정책 문서: `docs/PRD.md`, `docs/UML.md`, `docs/recommendation_requirements.md`

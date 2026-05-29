# AlphaPick Architecture Cleanup & Normalization Document

본 문서는 AlphaPick MVP 코드베이스에서 타 프로젝트의 피트니스 관련 레거시 요소를 정화하고, PRD 및 UML 설계 사양에 맞춰 주식 분석 및 포트폴리오 로직을 정상화한 내역을 기록한 아키텍처 정규화 문서입니다.

---

## 1. 아키텍처 정화 내역 (Cleanup)

주식 분석 플랫폼인 AlphaPick 도메인의 순수성을 해치고 리소스를 점유하던 이전 피트니스 관련 프로젝트("Outfit")의 잔재 코드를 완전히 제거했습니다.

### 1.1. 백엔드 앱 및 핏스처 삭제
- **삭제 앱**: `catalog`(피트니스 코스), `workouts`(운동 기록), `reviews`(리뷰), `recommendations`(코스 위치 추천), `data_ingest`(피트니스 데이터 수집) 앱 폴더 전체를 물리적으로 삭제했습니다.
- **설정 정리**: `config/settings.py`의 `INSTALLED_APPS` 및 `config/urls.py`의 API 라우트 매핑에서 해당 앱들의 바인딩을 모두 제거했습니다.
- **핏스처 정리**: `fixtures/demo_catalog.json` 피트니스 샘플 데이터를 삭제했습니다.

### 1.2. 사용자 모델 및 어드민 정규화
- **불필요 필드 제거**: `accounts.User` 모델에서 `level`, `preferred_location`, `preferred_categories`, `onboarding_completed` 필드를 삭제했습니다.
- **어드민 보정**: `accounts/admin.py`에서 불필요한 필드 바인딩을 제거하고 `risk_type` 필드를 노출하도록 `AlphaPickUserAdmin`으로 리팩토링했습니다.
- **토큰 시리얼라이저 정화**: JWT 로그인용 시리얼라이저 이름을 `OutfitTokenObtainPairSerializer`에서 `AlphaPickTokenObtainPairSerializer`로 리네이밍했습니다.

### 1.3. 프론트엔드 레거시 파일 삭제
- `frontend/src/views`와 `frontend/src/components`에 방치되어 있던 피트니스 관련 미사용 화면/컴포넌트를 완전히 삭제했습니다.

---

## 2. 비즈니스 로직 정규화 내역 (Normalization)

PRD 스펙 대비 불일치하거나 누락되었던 금융 비즈니스 로직 및 UI 연동을 사양에 맞게 올바르게 정규화했습니다.

### 2.1. 사용자 투자 성향(`risk_type`) 연동
- `accounts.User` 모델에 주식 투자 성향을 저장할 `risk_type` 필드를 추가했습니다.
- 회원가입 및 토큰 발급 시 `risk_type`이 입출력 스펙에 정상 포함되도록 하였습니다.

### 2.2. 포트폴리오 편입 조건 정규화
- `stocks/services.py`에서 `MIN_COMPONENT_SCORE = 70` 기준을 유지하고, 공격형/중립형/안정형의 성향별 회사 가치·진입 타이밍·신뢰도 허들을 별도로 정의했습니다.
- `total_score` 단일 컷오프가 아니라 성향별 컴포넌트 허들을 통과한 종목만 포트폴리오 후보로 편입하도록 정리했습니다.

### 2.3. 현금 비중 및 Sector Cap 적용
- 편입 후보 수와 `marketDirection` 평균을 함께 보고 기본 현금 비중을 산정하도록 했습니다.
- 성향별 단일 섹터 최대 비중을 적용하고, 초과분은 다른 섹터에 재분배하며 남는 비중은 현금으로 전환하도록 했습니다.
- API 응답에 `cashWeight`, `baseCashWeight`, `sectorCashWeight`, `cashReasons`, `allocationItems`, `sectorCap`, `hurdles`를 포함했습니다.

### 2.4. 백테스트 현금 반영
- 포트폴리오 내 현금 비중은 가격 변동 없이 보유하는 것으로 처리해, 현금이 포함된 방어형 배분의 효과가 수익률 계산에 반영되도록 했습니다.

### 2.5. 프론트엔드 누락 기능 복구
- **관심종목(Watchlist) 토글**: 상세 화면 상단에 별표 버튼을 배치하여 사용자가 관심 종목을 추가/해제할 수 있도록 백엔드 API와 연동했습니다.
- **인증 라우트 복구**: 로그인, 회원가입, 마이페이지, 프로필 수정 화면을 `router/index.js`에 정상 등록하고, `AppHeader.vue`를 통해 로그인 상태에 따라 내비게이션 바가 다이내믹하게 변하도록 처리했습니다.
- **메인 포트폴리오 고도화**: Home 화면에 현금 비중, 현금 산정 사유, Sector Cap 조정 배지, 최종 자산 배분 막대를 추가했습니다.

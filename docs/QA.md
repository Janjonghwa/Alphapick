# QA 체크리스트

## 명령어 검증

```powershell
cd backend
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe makemigrations --check --dry-run
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py seed_alphapick --flush
.\.venv\Scripts\python.exe manage.py test stocks

cd ..\frontend
npm run build
```

## API 점검

```txt
GET /api/portfolio/today/
- 상태 코드 200
- 중립형 기준 회사 점수, 타이밍 점수, 신뢰도 허들을 통과한 종목만 편입
- 주식 비중과 현금 비중 합계가 100%에 근접
- allocationItems에 주식과 현금 항목 포함

GET /api/portfolio/today/?risk_type=aggressive
- 공격형 허들이 적용됨

GET /api/portfolio/today/?risk_type=stable
- 안정형 허들이 적용됨

GET /api/stocks/
- 상태 코드 200
- 종목 코드 중복 없음

GET /api/stocks/{ticker}/report/
- 상태 코드 200
- 가격 시계열, 점수 카드, 기술 지표, 재무 지표, 뉴스/공시 데이터 포함

POST /api/stocks/{ticker}/ai-comment/
- 상태 코드 200
- 긍정 요인, 주의 요인, 종합 의견 포함
```

## 화면 점검

- `/`: 기본 대시보드가 표시된다.
- AlphaPick 로고 클릭 시 `/`로 이동한다.
- `/portfolio`: 오늘의 포트폴리오 편입 종목 전체가 표시된다.
- 사이드바에 백테스트 메뉴가 표시되지 않는다.
- 기본 대시보드에 백테스트 요약 영역이 표시되지 않는다.
- `/stocks`: 종목 검색 화면이 표시된다.
- `/stocks/{ticker}`: 종목 리포트가 표시된다.

## 발표 전 확인 사항

- 백엔드 데이터가 비어 있으면 `seed_alphapick --flush`를 실행한다.
- 프론트가 API에 연결되지 않으면 백엔드 주소와 `VITE_API_BASE_URL`을 확인한다.
- 서비스는 투자 자문이 아니라 교육용 분석 도구임을 명확히 안내한다.

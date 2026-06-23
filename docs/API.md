# API 문서

본 문서는 AlphaPick 프론트엔드가 사용하는 주요 API를 화면 흐름 기준으로 정리한 문서입니다. 정식 OpenAPI/Swagger 명세가 아니라, 개발과 발표에서 빠르게 확인하기 위한 경량 API 문서입니다.

## 기본 정보

| 항목 | 값 |
|---|---|
| 기본 API 주소 | `http://127.0.0.1:8000/api` |
| 프론트 환경 변수 | `VITE_API_BASE_URL` |
| 기본 응답 형식 | JSON |
| 인증 방식 | JWT Bearer Token |
| 기본 페이지네이션 | DRF PageNumberPagination, `page`, `page_size` |

인증이 필요한 요청은 아래 헤더를 포함합니다.

```txt
Authorization: Bearer {access_token}
```

## 화면별 API 매핑

| 화면 | 프론트 경로 | 주요 API |
|---|---|---|
| 기본 대시보드 | `/` | `GET /portfolio/today/` |
| 오늘의 포트폴리오 | `/portfolio` | `GET /portfolio/today/` |
| 종목 검색 | `/stocks` | `GET /stocks/`, `GET /themes/` |
| 종목 리포트 | `/stocks/:ticker` | `GET /stocks/{ticker}/report/`, `POST /stocks/{ticker}/ai-comment/` |
| 커뮤니티 | `/community` | `GET /community/posts/`, `POST /community/posts/`, `GET /community/users/` |
| 종목 커뮤니티 | `/stocks/:ticker/community` | `GET /stocks/{ticker}/report/`, `GET /community/posts/?stock={ticker}` |
| 인증 | `/login`, `/register`, `/mypage` | `POST /auth/login/`, `POST /auth/register/`, `GET/PATCH /users/me/` |

## 인증 API

### 회원가입

| 항목 | 내용 |
|---|---|
| Method | `POST` |
| URL | `/auth/register/` |
| 인증 | 불필요 |

요청 본문:

```json
{
  "username": "user1",
  "password": "password",
  "password2": "password",
  "email": "user1@example.com"
}
```

응답 핵심 필드:

| 필드 | 설명 |
|---|---|
| `id` | 사용자 ID |
| `username` | 사용자명 |
| `email` | 이메일 |

### 로그인

| 항목 | 내용 |
|---|---|
| Method | `POST` |
| URL | `/auth/login/` |
| 인증 | 불필요 |

요청 본문:

```json
{
  "username": "user1",
  "password": "password"
}
```

응답 핵심 필드:

| 필드 | 설명 |
|---|---|
| `access` | API 인증용 access token |
| `refresh` | 토큰 재발급용 refresh token |
| `user` | 로그인 사용자 정보 |

### 토큰 재발급

| 항목 | 내용 |
|---|---|
| Method | `POST` |
| URL | `/auth/refresh/` |
| 인증 | 불필요 |

요청 본문:

```json
{
  "refresh": "{refresh_token}"
}
```

### 내 정보 조회/수정

| 항목 | 내용 |
|---|---|
| Method | `GET`, `PATCH` |
| URL | `/users/me/` |
| 인증 | 필요 |

수정 요청 예시:

```json
{
  "nickname": "알파픽유저",
  "bio": "관심 종목을 분석합니다."
}
```

## 포트폴리오 API

### 오늘의 포트폴리오 조회

| 항목 | 내용 |
|---|---|
| Method | `GET` |
| URL | `/portfolio/today/` |
| 인증 | 선택 |

쿼리 파라미터:

| 이름 | 필수 | 설명 |
|---|---|---|
| `risk_type` | 선택 | `neutral`, `aggressive`, `stable` |

요청 예시:

```txt
GET /api/portfolio/today/?risk_type=neutral
```

응답 핵심 필드:

| 필드 | 설명 |
|---|---|
| `baseDate` | 데이터 기준일 |
| `riskType` | 투자 성향 |
| `portfolioScore` | 포트폴리오 점수 |
| `cashWeight` | 현금 비중 |
| `items` | 편입 종목 목록 |
| `watchCandidates` | 관찰 후보 목록 |

`items` 주요 필드:

| 필드 | 설명 |
|---|---|
| `ticker` | 종목코드 |
| `name` | 종목명 |
| `sector` | AlphaPick 큰 테마 그룹 |
| `original_sector` | KRX/원천 데이터 기준 업종명 |
| `themes` | 연결된 2차 테마 목록 |
| `total_score` | 종합 점수 |
| `weight` | 추천 비중 |
| `key_reason` | 핵심 추천 사유 |
| `sector_cap_applied` | 섹터 비중 조정 여부 |
| `volume_surge_flag` | 거래량 급증 여부 |

### 포트폴리오 이력 조회

| 항목 | 내용 |
|---|---|
| Method | `GET` |
| URL | `/portfolio/history/` |
| 인증 | 선택 |

현재 사용자 화면에서는 직접 노출하지 않는 참고 API입니다.

### 백테스트 요약 조회

| 항목 | 내용 |
|---|---|
| Method | `GET` |
| URL | `/portfolio/backtest/` |
| 인증 | 선택 |

백테스트 화면은 프론트엔드에서 제거되었지만, 백엔드 API는 참고용으로 남아 있습니다.

## 종목 API

### 종목 목록 조회

| 항목 | 내용 |
|---|---|
| Method | `GET` |
| URL | `/stocks/` |
| 인증 | 선택 |

쿼리 파라미터:

| 이름 | 필수 | 설명 |
|---|---|---|
| `q` | 선택 | 종목명 또는 종목코드 검색 |
| `min_score` | 선택 | 최소 점수 필터 |
| `sector` | 선택 | DB 업종명 필터 |
| `market` | 선택 | `KOSPI`, `KOSDAQ` 등 시장 필터 |
| `theme_group` | 선택 | 테마 그룹명 필터. 예: `조선·해운` |
| `theme` | 선택 | 2차 테마명 필터. 예: `대형 조선` |
| `page` | 선택 | 페이지 번호 |

요청 예시:

```txt
GET /api/stocks/?q=삼성&min_score=70
GET /api/stocks/?theme_group=조선·해운
GET /api/stocks/?theme=대형%20조선
```

응답 핵심 필드:

| 필드 | 설명 |
|---|---|
| `count` | 전체 개수 |
| `next` | 다음 페이지 URL |
| `previous` | 이전 페이지 URL |
| `results` | 종목 목록 |

`results` 주요 필드:

| 필드 | 설명 |
|---|---|
| `ticker` | 종목코드 |
| `name` | 종목명 |
| `sector` | AlphaPick 큰 테마 그룹 |
| `original_sector` | KRX/원천 데이터 기준 업종명 |
| `industry` | 산업 |
| `primary_theme` | 대표 2차 테마 |
| `themes` | 연결된 2차 테마 목록 |
| `theme_groups` | 연결된 큰 테마 그룹 목록 |
| `latest_score` | 최근 종합 점수 |
| `current_price` | 현재가 또는 최근 종가 |
| `key_reason` | 핵심 사유 |

### 테마 그룹 목록 조회

종목 검색 화면의 좌측 섹터·테마 패널에서 사용합니다.

| 항목 | 내용 |
|---|---|
| Method | `GET` |
| URL | `/themes/` |
| 인증 | 선택 |
| 페이지네이션 | 없음 |

응답 예시:

```json
[
  {
    "id": 1,
    "name": "조선·해운",
    "icon": "⚓",
    "stock_count": 23,
    "themes": [
      { "id": 1, "name": "대형 조선", "stock_count": 9 },
      { "id": 2, "name": "조선 기자재", "stock_count": 5 }
    ]
  }
]
```

테마 데이터는 `seed_themes` 관리 명령어가 `ThemeGroup`, `Theme`, `StockTheme` 테이블에 적재합니다. 현재 구조는 원문 테마 추출본으로 매핑 가능한 종목을 먼저 연결하고, 남은 종목은 DB 업종/종목명 기반 보정 규칙으로 `기타` 또는 관련 테마에 배치합니다.

### 종목 리포트 조회

| 항목 | 내용 |
|---|---|
| Method | `GET` |
| URL | `/stocks/{ticker}/report/` |
| 인증 | 선택 |

응답 핵심 필드:

| 필드 | 설명 |
|---|---|
| `stock` | 종목 기본 정보 |
| `score` | 점수 스냅샷과 점수 카드 |
| `financialMetric` | 재무 지표 |
| `priceSeries` | 가격 시계열 |
| `investmentNotice` | 투자 유의 문구 |

### 가격 시계열 조회

| 항목 | 내용 |
|---|---|
| Method | `GET` |
| URL | `/stocks/{ticker}/prices/` |
| 인증 | 선택 |

종목 리포트의 차트 데이터로 사용할 수 있는 가격 시계열을 반환합니다.

### AI 코멘트 생성/조회

| 항목 | 내용 |
|---|---|
| Method | `POST` |
| URL | `/stocks/{ticker}/ai-comment/` |
| 인증 | 선택 |

요청 본문:

```json
{
  "risk_type": "neutral"
}
```

응답 핵심 필드:

| 필드 | 설명 |
|---|---|
| `positive` | 긍정 요인 |
| `negative` | 주의 요인 |
| `summary` | 종합 의견 |

## 관심 종목 API

### 내 관심 종목 조회

| 항목 | 내용 |
|---|---|
| Method | `GET` |
| URL | `/watchlist/` |
| 인증 | 필요 |

### 관심 종목 추가

| 항목 | 내용 |
|---|---|
| Method | `POST` |
| URL | `/watchlist/{ticker}/` |
| 인증 | 필요 |

### 관심 종목 삭제

| 항목 | 내용 |
|---|---|
| Method | `DELETE` |
| URL | `/watchlist/{ticker}/` |
| 인증 | 필요 |

## 커뮤니티 API

### 게시글 목록 조회

| 항목 | 내용 |
|---|---|
| Method | `GET` |
| URL | `/community/posts/` |
| 인증 | 선택 |

쿼리 파라미터:

| 이름 | 필수 | 설명 |
|---|---|---|
| `stock` | 선택 | 특정 종목코드 게시글 필터 |
| `author` | 선택 | 작성자 필터 |
| `following` | 선택 | 팔로우 중인 사용자 게시글 필터 |
| `search` | 선택 | 제목/본문 검색 |

### 게시글 작성

| 항목 | 내용 |
|---|---|
| Method | `POST` |
| URL | `/community/posts/` |
| 인증 | 필요 |

요청 본문:

```json
{
  "stock": "005930.KS",
  "title": "삼성전자 의견",
  "content": "수급과 모멘텀을 지켜보고 있습니다."
}
```

### 게시글 좋아요 토글

| 항목 | 내용 |
|---|---|
| Method | `POST` |
| URL | `/community/posts/{post_id}/like/` |
| 인증 | 필요 |

응답 핵심 필드:

| 필드 | 설명 |
|---|---|
| `liked` | 좋아요 여부 |
| `likes_count` | 좋아요 수 |

### 댓글 작성

| 항목 | 내용 |
|---|---|
| Method | `POST` |
| URL | `/community/posts/{post_id}/comments/` |
| 인증 | 필요 |

요청 본문:

```json
{
  "content": "동의합니다."
}
```

### 댓글 삭제

| 항목 | 내용 |
|---|---|
| Method | `DELETE` |
| URL | `/community/comments/{comment_id}/` |
| 인증 | 필요 |

### 커뮤니티 사용자 목록

| 항목 | 내용 |
|---|---|
| Method | `GET` |
| URL | `/community/users/` |
| 인증 | 선택 |

### 팔로우 토글

| 항목 | 내용 |
|---|---|
| Method | `POST` |
| URL | `/community/users/{user_id}/follow/` |
| 인증 | 필요 |

응답 핵심 필드:

| 필드 | 설명 |
|---|---|
| `following` | 팔로우 여부 |
| `followers_count` | 팔로워 수 |

## 상태 코드

| 상태 코드 | 의미 |
|---|---|
| `200 OK` | 조회/수정 성공 |
| `201 Created` | 생성 성공 |
| `204 No Content` | 삭제 성공 |
| `400 Bad Request` | 요청 값 오류 |
| `401 Unauthorized` | 인증 필요 또는 토큰 오류 |
| `403 Forbidden` | 권한 없음 |
| `404 Not Found` | 리소스 없음 |
| `500 Internal Server Error` | 서버 오류 |

## 문서화 범위

- 이 문서는 현재 프론트엔드 화면과 백엔드 URL 기준의 경량 API 문서입니다.
- 정식 Swagger/OpenAPI 스키마가 필요한 경우 `drf-spectacular` 또는 `drf-yasg` 도입을 검토할 수 있습니다.
- 현재 프로젝트 제출과 발표 목적에서는 본 문서와 README의 주요 API 표를 기준 문서로 사용합니다.

# AlphaPick MVP

AlphaPick is a Django/DRF + Vue 3 MVP for a score-based stock portfolio recommendation service.

The app scores each stock report first, then builds today's alpha portfolio from stocks whose `total_score` is at least 70. Portfolio weights are calculated in proportion to the score above 70, and the portfolio is designed as a daily rebalance recommendation.

## Core Features

- Today's alpha portfolio: only stocks with `total_score >= 70`, `company_score >= 60`, `timing_score >= 60`, and `reliability_score >= 70`
- Score-above-threshold proportional portfolio weights
- Stock score report with headline, timing cards, chart data, CAN SLIM, score cards, financial/technical indicators, news, and disclosures
- Watch candidates when a stock misses the 70-point portfolio threshold
- MVP backtest comparing the recommended portfolio with KOSPI
- Local fixtures via `seed_alphapick`, so the project works without live stock APIs
- Risk-type portfolio variants and a cached AI 3-line stock comment endpoint for the final PRD flow

## Planning and Presentation Docs

- `docs/PRD.md`
- `docs/WBS_GANTT.md`
- `docs/UML.md`
- `docs/WIREFRAME.md`
- `docs/PRESENTATION_SCRIPT.md`
- `docs/QA.md`

## Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py seed_alphapick --flush
.\.venv\Scripts\python.exe manage.py runserver
```

To replace the fixture data with real KOSPI daily prices, use the pykrx seed command:

```powershell
cd backend
.\.venv\Scripts\python.exe manage.py seed_pykrx --market KOSPI --days 365 --flush
```

Useful test options:

```powershell
.\.venv\Scripts\python.exe manage.py seed_pykrx --tickers 005930,000660 --days 365 --sleep 0 --flush
.\.venv\Scripts\python.exe manage.py seed_pykrx --market KOSPI --days 365 --limit 30 --sleep 0.2 --flush
```

`seed_pykrx` first tries pykrx's market ticker list. If that endpoint returns empty, it falls back to the KRX KIND listed-company table for the KOSPI universe and still uses pykrx for each stock's OHLCV price history. The current implementation scores price, momentum, breakout, liquidity, drawdown, z-score and market breadth layers; pykrx fundamental endpoints are treated as optional because they can be unavailable depending on the local KRX endpoint response.

Main APIs:

```txt
GET /api/portfolio/today/
GET /api/portfolio/today/?risk_type=aggressive
GET /api/portfolio/history/
GET /api/portfolio/backtest/?benchmark=KOSPI
GET /api/stocks/
GET /api/stocks/{ticker}/report/
GET /api/stocks/{ticker}/prices/
POST /api/stocks/{ticker}/ai-comment/
POST /api/watchlist/{ticker}/
DELETE /api/watchlist/{ticker}/
```

## Frontend

```powershell
cd frontend
npm install
npm run dev
```

Set `VITE_API_BASE_URL` in `frontend/.env` if the backend is not running at `http://localhost:8000/api`.

## Verification

```powershell
cd backend
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py test stocks

cd ..\frontend
npm run build
```

## Investment Notice

This service is an educational analysis tool for the project. It is not financial advice, does not guarantee returns, and does not include real buy/sell order execution.

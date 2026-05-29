# Final QA Checklist

## Commands

```powershell
cd backend
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py seed_alphapick --flush
.\.venv\Scripts\python.exe manage.py test stocks

cd ..\frontend
npm run build
```

## API Smoke Checks

```txt
GET /api/portfolio/today/
- status 200
- neutral items pass company >= 70, timing >= 70, reliability >= 70
- stock weights + cashWeight sum to 100
- allocationItems includes stock allocation and cash when cashWeight > 0
- `?risk_type=aggressive|neutral|stable` returns the selected risk type

GET /api/stocks/
- status 200
- no duplicate tickers

GET /api/stocks/105560.KS/report/
- status 200
- 365 price points
- score cards, technical indicators, financial indicators, news/disclosures exist

POST /api/stocks/105560.KS/ai-comment/
- status 200
- positive, negative, conclusion each exist

GET /api/portfolio/backtest/
- status 200
- non-empty series
```

## Presentation Risks

- If the backend has no data, run `seed_alphapick --flush`.
- If frontend cannot connect, verify `VITE_API_BASE_URL` or run the backend at `http://localhost:8000/api`.
- The service is educational and must be presented as analysis support, not investment advice.

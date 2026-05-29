# Presentation Script

## 1. Opening

AlphaPick solves the problem of choosing a few high-conviction stocks from a large stock universe. The main product is not a simple stock list. It is today's alpha portfolio, built only from stocks that pass risk-type-specific company value, entry timing, and reliability hurdles.

## 2. Demo Flow

1. Run the backend and frontend.
2. Open the home page.
3. Explain the portfolio policy:
   - neutral hurdle: company 70, timing 70, reliability 70
   - aggressive/stable hurdles
   - cash allocation for weak markets
   - sector cap and redistribution
   - daily rebalance
   - eligibility-score-proportional stock weights
4. Click a portfolio item such as SK Hynix, Samsung Electronics, or KB Financial.
5. Show the stock report:
   - headline
   - timing cards
   - price chart
   - total score
   - score cards
   - technical and financial indicators
   - news/disclosures
6. Move to stock search and show that watch candidates exist below the threshold.
7. Move to backtest and compare the MVP portfolio with KOSPI.

## 3. Key Differentiation

- Recommendations are portfolio-first, not list-first.
- Each recommendation has an explainable score report.
- The risk-type hurdle policy prevents weak candidates from entering the main portfolio.
- Cash allocation and Sector Cap make the recommendation behave like a portfolio, not a leaderboard.
- Fixtures make evaluation repeatable without external API risk.

## 4. Closing

This MVP proves the full flow from data ingestion to scoring, portfolio construction, score report explanation, and backtest validation. The next step would be replacing seed data with live FinanceDataReader, pykrx, OpenDART, and news APIs.

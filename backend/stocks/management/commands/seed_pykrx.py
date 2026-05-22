import math
import re
import time
import warnings
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from html.parser import HTMLParser

import numpy as np
import pandas as pd
import requests
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

warnings.filterwarnings("ignore", message="pkg_resources is deprecated")
from pykrx import stock as krx_stock  # noqa: E402

from stocks.models import (
    AICommentCache,
    FinancialMetric,
    PortfolioItem,
    PortfolioRun,
    PriceDaily,
    ScoreSnapshot,
    Stock,
    Watchlist,
)
from stocks.services import ensure_portfolio_run


KOSPI_CORP_LIST_URL = "https://kind.krx.co.kr/corpgeneral/corpList.do?method=download&marketType=stockMkt"
DEFAULT_MIN_TRADING_VALUE = 5_000_000_000


class CorpListParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_cell = False
        self.cell = []
        self.row = []
        self.rows = []

    def handle_starttag(self, tag, attrs):
        if tag in {"td", "th"}:
            self.in_cell = True
            self.cell = []

    def handle_data(self, data):
        if self.in_cell:
            self.cell.append(data)

    def handle_endtag(self, tag):
        if tag in {"td", "th"} and self.in_cell:
            value = re.sub(r"\s+", " ", "".join(self.cell)).strip()
            self.row.append(value)
            self.in_cell = False
        elif tag == "tr" and self.row:
            self.rows.append(self.row)
            self.row = []


@dataclass
class TickerMeta:
    ticker: str
    name: str
    sector: str
    industry: str


@dataclass
class CollectedStock:
    meta: TickerMeta
    prices: pd.DataFrame
    metrics: dict


def clamp(value, low=0, high=100):
    if value is None or pd.isna(value) or math.isinf(value):
        return low
    return max(low, min(high, float(value)))


def to_yyyymmdd(value):
    if isinstance(value, str):
        return value.replace("-", "")
    return value.strftime("%Y%m%d")


def parse_base_date(value):
    if value:
        return datetime.strptime(value.replace("-", ""), "%Y%m%d").date()
    return date.today()


def fetch_kind_kospi_list():
    response = requests.get(KOSPI_CORP_LIST_URL, timeout=30)
    response.raise_for_status()
    response.encoding = "euc-kr"

    parser = CorpListParser()
    parser.feed(response.text)
    if len(parser.rows) < 2:
        raise CommandError("KIND KOSPI corp list returned no rows.")

    result = []
    for row in parser.rows[1:]:
        if len(row) < 4:
            continue
        ticker = row[2].zfill(6)
        result.append(
            TickerMeta(
                ticker=ticker,
                name=row[0],
                sector=row[3] or "KOSPI",
                industry=row[4] if len(row) > 4 else "",
            )
        )
    return result


def fetch_pykrx_ticker_list(base_date, market):
    tickers = krx_stock.get_market_ticker_list(to_yyyymmdd(base_date), market=market)
    result = []
    for ticker in tickers:
        name = krx_stock.get_market_ticker_name(ticker) or ticker
        result.append(TickerMeta(ticker=ticker, name=name, sector=market, industry=""))
    return result


def resolve_tickers(options):
    if options["tickers"]:
        return [
            TickerMeta(ticker=ticker.strip().zfill(6), name=ticker.strip().zfill(6), sector=options["market"], industry="")
            for ticker in options["tickers"].split(",")
            if ticker.strip()
        ]

    if options["tickers_file"]:
        rows = []
        frame = pd.read_csv(options["tickers_file"], encoding="utf-8-sig")
        for _, row in frame.iterrows():
            ticker = str(row.get("ticker") or row.get("종목코드") or row.get("code") or "").zfill(6)
            if not ticker or ticker == "000nan":
                continue
            rows.append(
                TickerMeta(
                    ticker=ticker,
                    name=str(row.get("name") or row.get("회사명") or ticker),
                    sector=str(row.get("sector") or row.get("업종") or options["market"]),
                    industry=str(row.get("industry") or row.get("주요제품") or ""),
                )
            )
        return rows

    try:
        pykrx_rows = fetch_pykrx_ticker_list(options["base_date"], options["market"])
        if pykrx_rows:
            return pykrx_rows
    except Exception:
        pykrx_rows = []

    if options["market"] == "KOSPI":
        return fetch_kind_kospi_list()

    raise CommandError(
        "pykrx ticker list is empty. Pass --tickers-file or --tickers for this market."
    )


def normalize_ohlcv(raw):
    if raw.empty or len(raw.columns) < 5:
        return pd.DataFrame()

    frame = raw.copy()
    frame = frame.iloc[:, :5]
    frame.columns = ["open", "high", "low", "close", "volume"]
    frame = frame.dropna()
    for column in frame.columns:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    frame = frame.dropna()
    frame = frame[(frame["open"] > 0) & (frame["high"] > 0) & (frame["low"] > 0) & (frame["close"] > 0)]
    frame.index = pd.to_datetime(frame.index)
    return frame


def rsi(series, period=14):
    diff = series.diff()
    gain = diff.clip(lower=0).rolling(period).mean()
    loss = (-diff.clip(upper=0)).rolling(period).mean()
    rs = gain / loss.replace(0, np.nan)
    value = 100 - (100 / (1 + rs))
    return value.fillna(50)


def hurst_exponent(series):
    values = np.asarray(series.dropna().tail(180), dtype=float)
    if len(values) < 80 or np.std(values) == 0:
        return 0.5
    lags = range(2, 20)
    tau = [np.std(values[lag:] - values[:-lag]) for lag in lags]
    tau = np.asarray([item for item in tau if item > 0], dtype=float)
    if len(tau) < 5:
        return 0.5
    slope = np.polyfit(np.log(list(lags)[: len(tau)]), np.log(tau), 1)[0]
    return clamp(slope * 2, 0, 1)


def trading_value_score(value):
    if value >= 50_000_000_000:
        return 100
    if value >= 20_000_000_000:
        return 88
    if value >= 10_000_000_000:
        return 78
    if value >= 5_000_000_000:
        return 66
    if value >= 1_000_000_000:
        return 45
    return 20


def score_from_return(value, scale=1.0):
    return clamp(50 + value * scale)


def signal_for(score, volume_surge, fail_safe):
    if fail_safe:
        return "WATCH (Fail-Safe Active)"
    if score >= 80:
        return "STRONG LEADER"
    if score >= 74:
        return "LEADER"
    if score >= 70:
        return "WATCH LIST - Accumulate"
    if score >= 60:
        return "NEUTRAL - Hold"
    if score >= 45:
        return "CAUTION - Reduce"
    return "LAGGARD - Avoid"


def pct_change(close, days):
    if len(close) <= days:
        return 0
    start = close.iloc[-days - 1]
    if not start:
        return 0
    return (close.iloc[-1] / start - 1) * 100


def build_price_frame(raw):
    frame = normalize_ohlcv(raw)
    if frame.empty:
        return frame

    close = frame["close"]
    volume = frame["volume"]
    frame["ema20"] = close.ewm(span=20, adjust=False).mean()
    frame["ema50"] = close.ewm(span=50, adjust=False).mean()
    frame["ema200"] = close.ewm(span=200, adjust=False).mean()
    ma20 = close.rolling(20).mean()
    std20 = close.rolling(20).std()
    frame["bb_upper"] = ma20 + std20 * 2
    frame["bb_lower"] = ma20 - std20 * 2
    direction = np.sign(close.diff()).fillna(0)
    frame["obv"] = (direction * volume).cumsum()
    return frame


def collect_metrics(frame, min_trading_value):
    close = frame["close"]
    high = frame["high"]
    volume = frame["volume"]
    daily_return = close.pct_change().replace([np.inf, -np.inf], np.nan).dropna()
    current_price = float(close.iloc[-1])
    high_52w = float(high.tail(252).max())
    distance_to_high = (high_52w - current_price) / high_52w * 100 if high_52w else 100
    avg_trading_value_20 = float((close * volume).tail(20).mean())
    avg_volume_20 = float(volume.tail(20).mean()) or 1
    volume_ratio = float(volume.iloc[-1] / avg_volume_20)
    z_std = close.tail(20).std()
    z_score = float((current_price - close.tail(20).mean()) / z_std) if z_std else 0
    drawdown = (close / close.cummax() - 1).min() * 100
    volatility = daily_return.tail(120).std() * math.sqrt(252) * 100 if len(daily_return) else 0
    obv = frame["obv"]
    obv_trend = pct_change(obv.abs() + 1, min(60, max(1, len(obv) - 2)))
    rsi_value = float(rsi(close).iloc[-1])

    return {
        "current_price": current_price,
        "return_21": pct_change(close, 21),
        "return_63": pct_change(close, 63),
        "return_126": pct_change(close, 126),
        "return_252": pct_change(close, min(252, max(1, len(close) - 2))),
        "high_52w": high_52w,
        "distance_to_high": distance_to_high,
        "avg_trading_value_20": avg_trading_value_20,
        "volume_ratio": volume_ratio,
        "volume_surge": volume_ratio >= 2.0,
        "z_score": z_score,
        "mdd": float(drawdown),
        "volatility": float(volatility or 0),
        "obv_trend": float(obv_trend or 0),
        "rsi": rsi_value,
        "hurst": hurst_exponent(close),
        "above_ema20": current_price >= float(frame["ema20"].iloc[-1]),
        "above_ema50": current_price >= float(frame["ema50"].iloc[-1]),
        "above_ema200": current_price >= float(frame["ema200"].iloc[-1]) if not pd.isna(frame["ema200"].iloc[-1]) else False,
        "is_new_high": distance_to_high <= 3.0,
        "low_liquidity": avg_trading_value_20 < min_trading_value,
        "history_len": len(frame),
    }


def percentile_rank(value, values):
    finite = sorted(item for item in values if item is not None and not pd.isna(item))
    if not finite:
        return 50
    below = sum(1 for item in finite if item <= value)
    return int(round((below / len(finite)) * 99))


def score_stock(collected, rs_rank, market_direction):
    metrics = collected.metrics
    liquidity = trading_value_score(metrics["avg_trading_value_20"])
    inverse_vol = clamp(100 - metrics["volatility"])
    price_quality = clamp(70 - max(metrics["distance_to_high"] - 15, 0) * 1.5)
    value_quality = round(clamp(liquidity * 0.45 + inverse_vol * 0.30 + price_quality * 0.25), 1)

    annual_roe_proxy = round(clamp(50 + max(metrics["return_252"], -40) * 0.4 + liquidity * 0.15), 1)
    eps_acceleration = round(clamp(50 + metrics["return_63"] * 0.9 + (metrics["return_63"] - metrics["return_126"] / 2) * 0.35), 1)
    company_score = round(value_quality * 0.40 + annual_roe_proxy * 0.30 + eps_acceleration * 0.30, 1)

    momentum = round(
        clamp(
            rs_rank * 0.40
            + score_from_return(metrics["return_126"], 0.9) * 0.30
            + clamp(100 - metrics["distance_to_high"] * 3) * 0.30
        ),
        1,
    )
    trend_bonus = 12 if metrics["hurst"] > 0.5 else 0
    pivot = round(
        clamp(
            (72 if metrics["is_new_high"] else 48)
            + (10 if metrics["above_ema20"] else -8)
            + (8 if metrics["above_ema50"] else -6)
            + (6 if metrics["volume_surge"] else 0)
            + trend_bonus
        ),
        1,
    )
    smart_money = round(
        clamp(
            trading_value_score(metrics["avg_trading_value_20"]) * 0.45
            + clamp(metrics["volume_ratio"] * 30, 0, 100) * 0.35
            + score_from_return(metrics["obv_trend"], 0.6) * 0.20
        ),
        1,
    )
    timing_score = round(momentum * 0.40 + pivot * 0.30 + smart_money * 0.30, 1)

    mean_reversion = 82
    if metrics["z_score"] > 2.5:
        mean_reversion = 35
    elif metrics["z_score"] > 2.0:
        mean_reversion = 55
    elif metrics["z_score"] < -2.0:
        mean_reversion = 68

    drawdown_control = round(clamp(100 + metrics["mdd"] * 2.0 - max(metrics["volatility"] - 45, 0) * 0.7), 1)
    risk_layer = round(market_direction * 0.40 + mean_reversion * 0.30 + drawdown_control * 0.30, 1)
    reliability = round(
        clamp(min(metrics["history_len"] / 240 * 100, 100) * 0.65 + liquidity * 0.25 + 72 * 0.10),
        1,
    )

    total = company_score * 0.45 + timing_score * 0.55
    log = []
    if metrics["is_new_high"]:
        log.append("Price is within 3% of its 52-week high.")
    if metrics["hurst"] > 0.5:
        log.append("Hurst filter marks this as a trending price series.")
    if metrics["volume_surge"]:
        log.append("Volume ratio is above 2.0, so volume surge flag is on.")
    if metrics["z_score"] > 2.0:
        total *= 0.8
        log.append("Z-score is overheated; final score discounted by 20%.")
    elif risk_layer < 45:
        total *= 0.94
        log.append("Risk-control layer is weak; final score discounted by 6%.")
    elif risk_layer < 60:
        total *= 0.97
        log.append("Risk-control layer is below normal; final score discounted by 3%.")
    if metrics["mdd"] < -35:
        total -= 8
        log.append("Deep drawdown risk penalty applied.")
    if market_direction < 45:
        total *= 0.97
        log.append("Weak KOSPI breadth reduced the final score by 3%.")
    if reliability < 70:
        total *= 0.9
        log.append("Reliability below 70 reduced the final score.")

    fail_safe = metrics["history_len"] < 120 or reliability < 55
    if fail_safe:
        total = min(total, 55)
        log.append("Fail-safe: insufficient history/reliability capped the score.")

    total = round(clamp(total), 1)
    key_reasons = []
    if rs_rank >= 80:
        key_reasons.append(f"RS {rs_rank}")
    if metrics["distance_to_high"] <= 5:
        key_reasons.append("near 52w high")
    if metrics["return_63"] > 10:
        key_reasons.append("3M momentum")
    if metrics["volume_surge"]:
        key_reasons.append("volume surge")
    if not key_reasons:
        key_reasons.append("valid 1Y price data")

    warning = ""
    if metrics["z_score"] > 2:
        warning = "Short-term overheat risk is present."
    elif metrics["low_liquidity"]:
        warning = "Average trading value is below the liquidity threshold."
    elif metrics["mdd"] < -25:
        warning = "Drawdown risk is elevated."

    return {
        "total_score": total,
        "company_score": company_score,
        "timing_score": timing_score,
        "reliability_score": reliability,
        "value_quality": value_quality,
        "annual_roe_proxy": annual_roe_proxy,
        "eps_acceleration": eps_acceleration,
        "momentum": momentum,
        "pivot": pivot,
        "smart_money": smart_money,
        "risk_layer": risk_layer,
        "drawdown_control": drawdown_control,
        "market_direction": market_direction,
        "mean_reversion": mean_reversion,
        "fail_safe": fail_safe,
        "signal": signal_for(total, metrics["volume_surge"], fail_safe),
        "key_reason": " · ".join(key_reasons),
        "headline": f"{collected.meta.name} scores {total:.1f} from real KOSPI 1Y pykrx price data.",
        "verdict": "Recommend" if total >= 70 and not fail_safe and not metrics["low_liquidity"] else "Watch",
        "reason": "Real KOSPI daily prices were scored with momentum, breakout, smart-money and risk-control layers.",
        "warning": warning,
        "scoring_log": log,
        "rs_rank": rs_rank,
    }


class Command(BaseCommand):
    help = "Seed real KOSPI data through pykrx OHLCV and generate AlphaPick scores/portfolio."

    def add_arguments(self, parser):
        parser.add_argument("--market", default="KOSPI", choices=["KOSPI", "KOSDAQ"])
        parser.add_argument("--days", type=int, default=365)
        parser.add_argument("--end")
        parser.add_argument("--limit", type=int)
        parser.add_argument("--sleep", type=float, default=0.25)
        parser.add_argument("--flush", action="store_true")
        parser.add_argument("--tickers")
        parser.add_argument("--tickers-file")
        parser.add_argument("--min-trading-value", type=int, default=DEFAULT_MIN_TRADING_VALUE)

    def handle(self, *args, **options):
        base_date = parse_base_date(options["end"])
        options["base_date"] = base_date
        start_date = base_date - timedelta(days=options["days"])

        metas = resolve_tickers(options)
        if options["limit"]:
            metas = metas[: options["limit"]]
        if not metas:
            raise CommandError("No tickers resolved.")

        if options["flush"]:
            self.flush_data()

        self.stdout.write(f"Resolved {len(metas)} {options['market']} tickers. Collecting {options['days']} days...")
        collected = []
        skipped = []
        for index, meta in enumerate(metas, start=1):
            try:
                raw = krx_stock.get_market_ohlcv_by_date(to_yyyymmdd(start_date), to_yyyymmdd(base_date), meta.ticker)
                frame = build_price_frame(raw)
                if frame.empty or len(frame) < 30:
                    skipped.append((meta.ticker, "empty price history"))
                    continue
                metrics = collect_metrics(frame, options["min_trading_value"])
                if meta.name == meta.ticker:
                    meta.name = krx_stock.get_market_ticker_name(meta.ticker) or meta.ticker
                collected.append(CollectedStock(meta=meta, prices=frame, metrics=metrics))
            except Exception as exc:
                skipped.append((meta.ticker, str(exc)))
            if options["sleep"] and index < len(metas):
                time.sleep(options["sleep"])
            if index % 50 == 0:
                self.stdout.write(f"  collected {index}/{len(metas)}")

        if not collected:
            raise CommandError(f"No valid pykrx price histories. First skips: {skipped[:5]}")

        returns_252 = [item.metrics["return_252"] for item in collected]
        market_direction = round(clamp(50 + np.nanmedian([item.metrics["return_63"] for item in collected]) * 1.4), 1)
        scored = [
            (item, score_stock(item, percentile_rank(item.metrics["return_252"], returns_252), market_direction))
            for item in collected
        ]

        with transaction.atomic():
            for item, score in scored:
                self.save_stock(item, score, base_date, options["market"])
            run = ensure_portfolio_run(base_date)

        self.stdout.write(self.style.SUCCESS(
            f"Saved {len(scored)} stocks, skipped {len(skipped)}, portfolio items {run.items.count()}."
        ))
        if skipped:
            sample = ", ".join(f"{ticker}:{reason}" for ticker, reason in skipped[:5])
            self.stdout.write(f"Skipped sample: {sample}")

    def flush_data(self):
        Watchlist.objects.all().delete()
        AICommentCache.objects.all().delete()
        PortfolioItem.objects.all().delete()
        PortfolioRun.objects.all().delete()
        ScoreSnapshot.objects.all().delete()
        FinancialMetric.objects.all().delete()
        PriceDaily.objects.all().delete()
        Stock.objects.all().delete()

    def save_stock(self, item, score, base_date, market):
        stock_obj, _ = Stock.objects.update_or_create(
            ticker=f"{item.meta.ticker}.KS" if market == "KOSPI" else f"{item.meta.ticker}.KQ",
            defaults={
                "name": item.meta.name,
                "market": market,
                "sector": item.meta.sector or market,
                "industry": item.meta.industry or "",
                "primary_theme": item.meta.sector or market,
                "is_universe_included": True,
                "low_liquidity_flag": item.metrics["low_liquidity"],
                "is_active": True,
                "is_tradable": True,
            },
        )

        PriceDaily.objects.filter(stock=stock_obj).delete()
        prices = []
        for row_date, row in item.prices.iterrows():
            prices.append(
                PriceDaily(
                    stock=stock_obj,
                    date=row_date.date(),
                    open_price=int(row["open"]),
                    high_price=int(row["high"]),
                    low_price=int(row["low"]),
                    close_price=int(row["close"]),
                    volume=int(row["volume"]),
                    ema20=None if pd.isna(row["ema20"]) else float(row["ema20"]),
                    ema50=None if pd.isna(row["ema50"]) else float(row["ema50"]),
                    ema200=None if pd.isna(row["ema200"]) else float(row["ema200"]),
                    bb_upper=None if pd.isna(row["bb_upper"]) else float(row["bb_upper"]),
                    bb_lower=None if pd.isna(row["bb_lower"]) else float(row["bb_lower"]),
                    obv=None if pd.isna(row["obv"]) else float(row["obv"]),
                )
            )
        PriceDaily.objects.bulk_create(prices, batch_size=1000)

        FinancialMetric.objects.update_or_create(
            stock=stock_obj,
            base_date=base_date,
            defaults={
                "per": None,
                "pbr": None,
                "roe": None,
                "eps_growth": score["eps_acceleration"],
                "operating_margin": None,
                "debt_ratio": None,
                "dividend_yield": None,
                "market_cap": None,
                "target_price": None,
                "current_price": int(item.metrics["current_price"]),
                "payload": {
                    "source": "pykrx_ohlcv",
                    "avg_trading_value_20": round(item.metrics["avg_trading_value_20"], 0),
                    "fundamental_status": "pykrx fundamentals unavailable in this environment",
                },
            },
        )

        ScoreSnapshot.objects.update_or_create(
            stock=stock_obj,
            base_date=base_date,
            defaults={
                "total_score": score["total_score"],
                "company_score": score["company_score"],
                "timing_score": score["timing_score"],
                "reliability_score": score["reliability_score"],
                "financial_health_score": score["annual_roe_proxy"],
                "valuation_score": score["value_quality"],
                "growth_score": score["eps_acceleration"],
                "momentum_score": score["momentum"],
                "technical_timing_score": score["pivot"],
                "supply_score": score["smart_money"],
                "sentiment_score": score["risk_layer"],
                "headline": score["headline"],
                "verdict": score["verdict"],
                "signal": score["signal"],
                "key_reason": score["key_reason"],
                "rs_rank": score["rs_rank"],
                "rsi": round(item.metrics["rsi"], 1),
                "volume_ratio": round(item.metrics["volume_ratio"], 2),
                "target_upside": None,
                "target_upside_clipped": False,
                "consensus": "PRICE_ONLY",
                "confidence": "MID" if score["reliability_score"] >= 70 else "LOW",
                "fail_safe_flag": score["fail_safe"],
                "volume_surge_flag": item.metrics["volume_surge"],
                "area_scores": {
                    "valueQuality": score["value_quality"],
                    "annualRoeProxy": score["annual_roe_proxy"],
                    "epsAcceleration": score["eps_acceleration"],
                    "leadershipMomentum": score["momentum"],
                    "pivotBreakout": score["pivot"],
                    "smartMoney": score["smart_money"],
                    "marketDirection": score["market_direction"],
                    "meanReversion": score["mean_reversion"],
                    "drawdownControl": score["drawdown_control"],
                },
                "scoring_log": score["scoring_log"],
                "reason": score["reason"],
                "warning": score["warning"],
                "summary_metrics": [
                    {"label": "RS Rank", "value": score["rs_rank"], "tone": "good" if score["rs_rank"] >= 70 else "neutral"},
                    {"label": "3M Return", "value": f"{item.metrics['return_63']:.1f}%", "tone": "good" if item.metrics["return_63"] > 0 else "bad"},
                    {"label": "RSI", "value": f"{item.metrics['rsi']:.1f}", "tone": "neutral"},
                    {"label": "Avg Trading Value", "value": f"{item.metrics['avg_trading_value_20'] / 100000000:.0f}억", "tone": "good" if not item.metrics["low_liquidity"] else "bad"},
                ],
                "timing_cards": [
                    {"title": "Trend Filter", "score": round(item.metrics["hurst"] * 100, 1), "description": "Hurst exponent trend switch."},
                    {"title": "Breakout", "score": score["pivot"], "description": "52-week high proximity and EMA alignment."},
                    {"title": "Smart Money", "score": score["smart_money"], "description": "Volume ratio and OBV proxy."},
                ],
                "score_cards": [
                    {"title": "Value / Quality", "score": score["value_quality"], "description": "Liquidity and volatility-adjusted quality proxy."},
                    {"title": "Leadership Momentum", "score": score["momentum"], "description": "Relative strength and medium-term momentum."},
                    {"title": "Risk Control", "score": score["risk_layer"], "description": "Market breadth, z-score and drawdown control."},
                ],
                "can_slim": [
                    {"code": "C", "title": "Current Momentum", "score": score["eps_acceleration"]},
                    {"code": "A", "title": "Annual Quality Proxy", "score": score["annual_roe_proxy"]},
                    {"code": "M", "title": "Market Direction", "score": score["market_direction"]},
                ],
                "technical_indicators": [
                    {"label": "RSI(14)", "value": round(item.metrics["rsi"], 1), "status": "neutral"},
                    {"label": "Z-Score", "value": round(item.metrics["z_score"], 2), "status": "warning" if item.metrics["z_score"] > 2 else "normal"},
                    {"label": "MDD", "value": f"{item.metrics['mdd']:.1f}%", "status": "warning" if item.metrics["mdd"] < -25 else "normal"},
                    {"label": "Volume Ratio", "value": round(item.metrics["volume_ratio"], 2), "status": "good" if item.metrics["volume_surge"] else "normal"},
                ],
                "financial_indicators": [
                    {"label": "Fundamental Source", "value": "price-only fallback", "status": "warning"},
                    {"label": "Liquidity", "value": f"{item.metrics['avg_trading_value_20'] / 100000000:.0f}억", "status": "good" if not item.metrics["low_liquidity"] else "warning"},
                    {"label": "Reliability", "value": score["reliability_score"], "status": "good" if score["reliability_score"] >= 70 else "warning"},
                ],
                "news": [
                    {"title": "Live news scoring is not included in pykrx seed mode.", "sentiment": "neutral"}
                ],
                "disclosures": [
                    {"title": "pykrx OHLCV seed", "date": base_date.isoformat(), "source": "pykrx"}
                ],
            },
        )

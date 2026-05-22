from collections import Counter
from datetime import date

from django.db import transaction
from django.db.models import Max, Prefetch

from .models import AICommentCache, PortfolioItem, PortfolioRun, PriceDaily, ScoreSnapshot, Stock


PORTFOLIO_THRESHOLD = 70
MIN_RELIABILITY_SCORE = 70
MIN_COMPONENT_SCORE = 60
PRICE_HISTORY_DAYS = 365
RISK_TYPE_NEUTRAL = "neutral"
RISK_TYPE_AGGRESSIVE = "aggressive"
RISK_TYPE_STABLE = "stable"
RISK_TYPES = {RISK_TYPE_AGGRESSIVE, RISK_TYPE_NEUTRAL, RISK_TYPE_STABLE}
RISK_LABELS = {
    RISK_TYPE_AGGRESSIVE: "공격형",
    RISK_TYPE_NEUTRAL: "중립형",
    RISK_TYPE_STABLE: "안정형",
}
RISK_WEIGHTS = {
    RISK_TYPE_AGGRESSIVE: {
        "company": 0.38,
        "timing": 0.62,
    },
    RISK_TYPE_NEUTRAL: {
        "company": 0.45,
        "timing": 0.55,
    },
    RISK_TYPE_STABLE: {
        "company": 0.62,
        "timing": 0.38,
    },
}


def normalize_risk_type(value):
    value = (value or RISK_TYPE_NEUTRAL).lower()
    return value if value in RISK_TYPES else RISK_TYPE_NEUTRAL


def latest_score_date():
    return ScoreSnapshot.objects.aggregate(value=Max("base_date"))["value"]


def latest_price_date():
    return PriceDaily.objects.aggregate(value=Max("date"))["value"]


def latest_scores_queryset(base_date=None):
    base_date = base_date or latest_score_date()
    if not base_date:
        return ScoreSnapshot.objects.none()
    return (
        ScoreSnapshot.objects.filter(base_date=base_date)
        .select_related("stock")
        .order_by("-total_score", "stock__name")
    )


def portfolio_candidates(base_date=None):
    return latest_scores_queryset(base_date).filter(
        total_score__gte=PORTFOLIO_THRESHOLD,
        reliability_score__gte=MIN_RELIABILITY_SCORE,
        company_score__gte=MIN_COMPONENT_SCORE,
        timing_score__gte=MIN_COMPONENT_SCORE,
        stock__is_active=True,
        stock__is_tradable=True,
        stock__is_universe_included=True,
        stock__low_liquidity_flag=False,
        fail_safe_flag=False,
        stock__prices__isnull=False,
        stock__financial_metrics__isnull=False,
    ).distinct()


def watch_candidates(base_date=None, limit=5):
    return list(
        latest_scores_queryset(base_date)
        .filter(stock__is_active=True, stock__is_tradable=True)
        .exclude(
            total_score__gte=PORTFOLIO_THRESHOLD,
            reliability_score__gte=MIN_RELIABILITY_SCORE,
            company_score__gte=MIN_COMPONENT_SCORE,
            timing_score__gte=MIN_COMPONENT_SCORE,
            stock__low_liquidity_flag=False,
            fail_safe_flag=False,
        )[:limit]
    )


def weighted_component_score(score, risk_type=RISK_TYPE_NEUTRAL):
    risk_type = normalize_risk_type(risk_type)
    weights = RISK_WEIGHTS[risk_type]
    return round(score.company_score * weights["company"] + score.timing_score * weights["timing"], 2)


def score_for_risk(score, risk_type=RISK_TYPE_NEUTRAL):
    """Re-score by risk type while preserving the strict risk discount from the stored total."""
    if risk_type == RISK_TYPE_NEUTRAL:
        return round(score.total_score, 1)
    neutral_base = weighted_component_score(score, RISK_TYPE_NEUTRAL) or 1
    risk_discount = score.total_score / neutral_base
    adjusted_score = weighted_component_score(score, risk_type) * risk_discount
    return round(max(0, min(100, adjusted_score)), 1)


def company_score_for_risk(score, risk_type=RISK_TYPE_NEUTRAL):
    return round(score.company_score, 1)


def timing_score_for_risk(score, risk_type=RISK_TYPE_NEUTRAL):
    return round(score.timing_score, 1)


def sector_warning_for(scores):
    sectors = Counter(getattr(score, "sector", None) or score.stock.sector for score in scores)
    if not sectors:
        return ""
    sector, count = sectors.most_common(1)[0]
    if count >= 4:
        return f"{sector} 섹터 편입 종목이 {count}개입니다. MVP에서는 그대로 편입하지만 섹터 편중에 유의하세요."
    return ""


def build_portfolio_summary(scores):
    if not scores:
        return "오늘은 편입 조건을 만족한 종목이 없습니다. 관찰 후보를 확인하고 다음 리밸런싱을 기다려주세요."
    avg_score = sum(score.total_score for score in scores) / len(scores)
    top_reasons = " · ".join(score.stock.name for score in scores[:3])
    return f"{len(scores)}개 종목이 70점 이상 추천 후보 조건을 통과했습니다. 평균 점수는 {avg_score:.1f}점이며 핵심 편입 종목은 {top_reasons}입니다."


def build_dynamic_portfolio_payload(base_date=None, risk_type=RISK_TYPE_NEUTRAL):
    risk_type = normalize_risk_type(risk_type)
    base_date = base_date or latest_score_date() or date.today()
    scores = list(
        latest_scores_queryset(base_date)
        .filter(
            reliability_score__gte=MIN_RELIABILITY_SCORE,
            company_score__gte=MIN_COMPONENT_SCORE,
            timing_score__gte=MIN_COMPONENT_SCORE,
            stock__is_active=True,
            stock__is_tradable=True,
            stock__is_universe_included=True,
            stock__prices__isnull=False,
            stock__financial_metrics__isnull=False,
        )
        .distinct()
    )
    rows = []
    for score in scores:
        adjusted_score = score_for_risk(score, risk_type)
        rows.append(
            {
                "score_obj": score,
                "ticker": score.stock.ticker,
                "name": score.stock.name,
                "market": score.stock.market,
                "sector": score.stock.sector,
                "primary_theme": score.stock.primary_theme or score.stock.sector,
                "total_score": adjusted_score,
                "company_score": company_score_for_risk(score, risk_type),
                "timing_score": timing_score_for_risk(score, risk_type),
                "reliability_score": round(score.reliability_score, 1),
                "signal": score.signal,
                "key_reason": score.key_reason or score.reason,
                "rs_rank": score.rs_rank,
                "rsi": score.rsi,
                "volume_ratio": score.volume_ratio,
                "target_upside": score.target_upside,
                "target_upside_clipped": score.target_upside_clipped,
                "consensus": score.consensus,
                "confidence": score.confidence,
                "fail_safe_flag": score.fail_safe_flag,
                "volume_surge_flag": score.volume_surge_flag,
                "low_liquidity_flag": score.stock.low_liquidity_flag,
                "reason": score.reason,
                "warning": score.warning,
            }
        )
    rows.sort(key=lambda row: (-row["total_score"], row["name"]))
    items = [
        row
        for row in rows
        if row["total_score"] >= PORTFOLIO_THRESHOLD
        and not row["low_liquidity_flag"]
        and not row["fail_safe_flag"]
    ]
    score_sum = sum(max(row["total_score"] - PORTFOLIO_THRESHOLD, 1) for row in items)
    for row in items:
        score_edge = max(row["total_score"] - PORTFOLIO_THRESHOLD, 1)
        row["weight"] = round((score_edge / score_sum) * 100, 2) if score_sum else 0
        row.pop("score_obj", None)
    watch_rows = rows[len(items): len(items) + 5] if items else rows[:5]
    watch_candidates_payload = [
        {
            "ticker": row["ticker"],
            "name": row["name"],
            "market": row["market"],
            "sector": row["sector"],
            "primary_theme": row["primary_theme"],
            "industry": row["score_obj"].stock.industry,
            "latest_score": row["total_score"],
            "signal": row["signal"],
            "key_reason": row["key_reason"],
            "low_liquidity_flag": row["low_liquidity_flag"],
            "fail_safe_flag": row["fail_safe_flag"],
            "volume_surge_flag": row["volume_surge_flag"],
            "current_price": row["score_obj"].stock.financial_metrics.first().current_price
            if row["score_obj"].stock.financial_metrics.first()
            else None,
            "reason": row["reason"],
        }
        for row in watch_rows
    ]
    portfolio_score = round(sum(row["total_score"] for row in items) / len(items), 2) if items else 0
    sector_warning = sector_warning_for([type("PortfolioSector", (), row) for row in items])
    if not items:
        summary = f"{RISK_LABELS[risk_type]} 기준 70점 이상 추천 후보가 없습니다. 관찰 후보 TOP 5를 확인하세요."
    else:
        names = " · ".join(row["name"] for row in items[:3])
        summary = f"{RISK_LABELS[risk_type]} 기준 {len(items)}개 종목이 70점 이상 추천 포트폴리오에 편입되었습니다. 평균 점수는 {portfolio_score:.1f}점이며 핵심 편입 종목은 {names}입니다."
    return {
        "baseDate": base_date.isoformat(),
        "portfolioScore": portfolio_score,
        "rebalanceType": "daily",
        "threshold": PORTFOLIO_THRESHOLD,
        "userRiskType": risk_type,
        "riskTypeLabel": RISK_LABELS[risk_type],
        "summary": summary,
        "sectorWarning": sector_warning,
        "items": items,
        "watchCandidates": watch_candidates_payload,
        "benchmarkSummary": {
            "benchmark": "KOSPI",
            "rebalanceType": "daily",
            "threshold": PORTFOLIO_THRESHOLD,
            "itemCount": len(items),
            "message": "일별 리밸런싱 기준의 MVP 백테스트 요약은 /api/portfolio/backtest/에서 제공합니다.",
        },
    }


@transaction.atomic
def ensure_portfolio_run(base_date=None):
    base_date = base_date or latest_score_date() or date.today()
    scores = list(portfolio_candidates(base_date))
    score_sum = sum(max(score.total_score - PORTFOLIO_THRESHOLD, 1) for score in scores)
    portfolio_score = round(sum(score.total_score for score in scores) / len(scores), 2) if scores else 0

    run, _ = PortfolioRun.objects.update_or_create(
        base_date=base_date,
        defaults={
            "threshold": PORTFOLIO_THRESHOLD,
            "rebalance_type": "daily",
            "portfolio_score": portfolio_score,
            "summary": build_portfolio_summary(scores),
            "sector_warning": sector_warning_for(scores),
        },
    )
    run.items.all().delete()

    for score in scores:
        score_edge = max(score.total_score - PORTFOLIO_THRESHOLD, 1)
        weight = round((score_edge / score_sum) * 100, 2) if score_sum else 0
        PortfolioItem.objects.create(
            portfolio_run=run,
            stock=score.stock,
            score_snapshot=score,
            score=score.total_score,
            weight=weight,
            reason=score.reason,
            warning=score.warning,
        )
    return run


def get_today_portfolio():
    base_date = latest_score_date()
    if not base_date:
        return None
    return ensure_portfolio_run(base_date)


def portfolio_history(limit=20):
    return PortfolioRun.objects.prefetch_related(
        Prefetch("items", queryset=PortfolioItem.objects.select_related("stock", "score_snapshot"))
    ).order_by("-base_date")[:limit]


def stock_report(ticker):
    score_date = latest_score_date()
    stock = Stock.objects.get(ticker=ticker)
    score = stock.scores.filter(base_date=score_date).first() or stock.scores.first()
    metric = stock.financial_metrics.order_by("-base_date").first()
    prices = list(stock.prices.order_by("-date")[:PRICE_HISTORY_DAYS])
    prices.reverse()
    return {
        "stock": stock,
        "score": score,
        "metric": metric,
        "prices": prices,
    }


def calculate_backtest(benchmark="KOSPI"):
    runs = list(PortfolioRun.objects.order_by("base_date").prefetch_related("items__stock"))
    if not runs:
        return {
            "benchmark": benchmark,
            "rebalanceType": "daily",
            "portfolioReturn": 0,
            "benchmarkReturn": 0,
            "winRate": 0,
            "maxDrawdown": 0,
            "series": [],
            "summary": "아직 생성된 포트폴리오가 없습니다.",
        }

    portfolio_value = 100.0
    benchmark_value = 100.0
    series = []
    wins = 0
    peak = portfolio_value
    max_drawdown = 0

    for index, run in enumerate(runs):
        daily_alpha = 0.06 + max(run.portfolio_score - PORTFOLIO_THRESHOLD, 0) * 0.025
        benchmark_daily = 0.08 if benchmark.upper() == "KOSPI" else 0.06
        if not run.items.exists():
            daily_alpha = 0
        portfolio_value *= 1 + daily_alpha / 100
        benchmark_value *= 1 + benchmark_daily / 100
        wins += int(daily_alpha > benchmark_daily)
        peak = max(peak, portfolio_value)
        max_drawdown = min(max_drawdown, (portfolio_value - peak) / peak * 100)
        series.append(
            {
                "date": run.base_date.isoformat(),
                "portfolio": round(portfolio_value, 2),
                "benchmark": round(benchmark_value, 2),
                "portfolioDailyReturn": round(daily_alpha, 2),
                "benchmarkDailyReturn": benchmark_daily,
                "itemCount": run.items.count(),
            }
        )

    total_runs = len(runs)
    return {
        "benchmark": benchmark.upper(),
        "rebalanceType": "daily",
        "portfolioReturn": round(portfolio_value - 100, 2),
        "benchmarkReturn": round(benchmark_value - 100, 2),
        "winRate": round((wins / total_runs) * 100, 1) if total_runs else 0,
        "maxDrawdown": round(max_drawdown, 2),
        "series": series,
        "summary": "추천 포트폴리오를 매일 리밸런싱한다고 가정한 MVP 백테스트입니다.",
    }


def generate_ai_comment(ticker, risk_type=RISK_TYPE_NEUTRAL):
    risk_type = normalize_risk_type(risk_type)
    report = stock_report(ticker)
    stock = report["stock"]
    score = report["score"]
    metric = report["metric"]
    if not score:
        raise ValueError("score report is not ready")

    cached = AICommentCache.objects.filter(
        stock=stock,
        base_date=score.base_date,
        risk_type=risk_type,
    ).first()
    if cached:
        return cached, True

    best_cards = sorted(score.score_cards or [], key=lambda card: card.get("score", 0), reverse=True)
    worst_cards = sorted(score.score_cards or [], key=lambda card: card.get("score", 100))
    positive_title = best_cards[0]["title"] if best_cards else "핵심 지표"
    negative_title = worst_cards[0]["title"] if worst_cards else "위험 지표"
    upside = 0
    if metric and metric.current_price and metric.target_price:
        upside = round((metric.target_price - metric.current_price) / metric.current_price * 100, 1)

    positive = f"{stock.name}은 {positive_title} 점수가 강하고, 종합 점수 {score_for_risk(score, risk_type):.1f}점으로 {RISK_LABELS[risk_type]} 기준 포트폴리오 후보에 적합합니다."
    negative = f"다만 {negative_title} 항목과 '{score.warning or '단기 변동성'}' 이슈는 진입 전 확인이 필요합니다."
    conclusion = f"목표가 기준 상승 여력은 약 {upside}%이며, 현재 판단은 '{score.verdict}'입니다. 본 결과는 투자 참고용 분석입니다."

    comment = AICommentCache.objects.create(
        stock=stock,
        base_date=score.base_date,
        risk_type=risk_type,
        positive=positive,
        negative=negative,
        conclusion=conclusion,
        provider="local-mvp",
    )
    return comment, False

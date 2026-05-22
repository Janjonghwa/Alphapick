from datetime import date, timedelta
from math import sin

from django.core.management.base import BaseCommand
from django.db import transaction

from stocks.models import AICommentCache, FinancialMetric, PortfolioItem, PortfolioRun, PriceDaily, ScoreSnapshot, Stock, Watchlist
from stocks.services import ensure_portfolio_run


SAMPLE_STOCKS = [
    {
        "ticker": "000660.KS",
        "name": "SK하이닉스",
        "market": "KOSPI",
        "sector": "반도체",
        "industry": "메모리 반도체",
        "base_price": 201000,
        "trend": 640,
        "per": 12.8,
        "pbr": 2.1,
        "roe": 18.6,
        "eps_growth": 42.5,
        "operating_margin": 23.4,
        "debt_ratio": 76.0,
        "target_price": 238000,
        "target_upside_raw": 485.0,
        "foreign_flow": "+42.1만주",
        "institution_flow": "+18.9만주",
        "value_quality": 82,
        "annual_roe": 82,
        "eps_acceleration": 92,
        "leadership_momentum": 94,
        "pivot_breakout": 89,
        "smart_money": 80,
        "hurst": 76,
        "market_direction": 82,
        "mean_reversion": 65,
        "drawdown_control": 82,
        "reliability": 91,
        "primary_theme": "메모리·HBM",
        "volume_surge": True,
        "headline": "강한 주도주 흐름이지만 단기 과열은 확인해야 하는 추천 후보",
        "reason": "EPS 가속도와 주도주 모멘텀이 강하고 신고가 돌파 신호도 양호합니다.",
        "warning": "단기 상승 폭이 커서 평균 회귀 과열 경고를 함께 확인해야 합니다.",
    },
    {
        "ticker": "005930.KS",
        "name": "삼성전자",
        "market": "KOSPI",
        "sector": "반도체",
        "industry": "종합 반도체",
        "base_price": 84200,
        "trend": 210,
        "per": 13.6,
        "pbr": 1.4,
        "roe": 13.2,
        "eps_growth": 28.4,
        "operating_margin": 19.8,
        "debt_ratio": 28.0,
        "target_price": 97000,
        "foreign_flow": "+85.4만주",
        "institution_flow": "+11.3만주",
        "value_quality": 82,
        "annual_roe": 76,
        "eps_acceleration": 84,
        "leadership_momentum": 86,
        "pivot_breakout": 80,
        "smart_money": 88,
        "hurst": 72,
        "market_direction": 82,
        "mean_reversion": 72,
        "drawdown_control": 82,
        "reliability": 94,
        "headline": "균형 잡힌 퀄리티와 수급으로 70점 기준을 통과한 추천 후보",
        "reason": "퀄리티, EPS 개선, 외국인 수급이 고르게 받쳐주는 종목입니다.",
        "warning": "단기 모멘텀은 SK하이닉스보다 약해 비중은 점수 차이를 반영합니다.",
    },
    {
        "ticker": "005380.KS",
        "name": "현대차",
        "market": "KOSPI",
        "sector": "자동차",
        "industry": "완성차",
        "base_price": 247000,
        "trend": 260,
        "per": 6.4,
        "pbr": 0.72,
        "roe": 11.7,
        "eps_growth": 14.2,
        "operating_margin": 9.1,
        "debt_ratio": 145.0,
        "target_price": 286000,
        "foreign_flow": "+12.4만주",
        "institution_flow": "-2.1만주",
        "value_quality": 90,
        "annual_roe": 78,
        "eps_acceleration": 70,
        "leadership_momentum": 82,
        "pivot_breakout": 78,
        "smart_money": 72,
        "hurst": 68,
        "market_direction": 79,
        "mean_reversion": 70,
        "drawdown_control": 68,
        "reliability": 86,
        "primary_theme": "자율주행·전장",
        "low_liquidity": True,
        "headline": "저평가 매력과 타이밍이 동시에 살아난 경계선 추천 후보",
        "reason": "밸류에이션 매력과 주가 모멘텀은 양호하지만 기관 수급은 강하지 않습니다.",
        "warning": "환율과 업황 민감도가 높아 낙폭 위험도를 계속 확인해야 합니다.",
    },
    {
        "ticker": "105560.KS",
        "name": "KB금융",
        "market": "KOSPI",
        "sector": "금융",
        "industry": "은행 지주",
        "base_price": 152800,
        "trend": 310,
        "per": 8.3,
        "pbr": 0.76,
        "roe": 10.0,
        "eps_growth": 16.8,
        "operating_margin": 10.5,
        "debt_ratio": 1211.7,
        "target_price": 169125,
        "target_upside_raw": -18.0,
        "foreign_flow": "-36.8만주",
        "institution_flow": "+36.9만주",
        "value_quality": 90,
        "annual_roe": 70,
        "eps_acceleration": 66,
        "leadership_momentum": 76,
        "pivot_breakout": 70,
        "smart_money": 58,
        "hurst": 62,
        "market_direction": 80,
        "mean_reversion": 78,
        "drawdown_control": 72,
        "reliability": 88,
        "primary_theme": "은행·금융지주",
        "headline": "밸류는 매력적이지만 수급 약화로 추천 기준 직전의 관찰 후보",
        "reason": "저평가 매력은 크지만 외국인 수급과 스마트머니 점수가 부족합니다.",
        "warning": "최근 외국인 수급 약화가 이어지면 추천 포트폴리오 편입이 어렵습니다.",
    },
    {
        "ticker": "035420.KS",
        "name": "NAVER",
        "market": "KOSPI",
        "sector": "인터넷",
        "industry": "플랫폼",
        "base_price": 214000,
        "trend": 110,
        "per": 22.1,
        "pbr": 1.32,
        "roe": 8.9,
        "eps_growth": 18.4,
        "operating_margin": 15.8,
        "debt_ratio": 58.0,
        "target_price": 242000,
        "foreign_flow": "+5.2만주",
        "institution_flow": "+7.0만주",
        "value_quality": 62,
        "annual_roe": 54,
        "eps_acceleration": 72,
        "leadership_momentum": 82,
        "pivot_breakout": 78,
        "smart_money": 72,
        "hurst": 66,
        "market_direction": 75,
        "mean_reversion": 62,
        "drawdown_control": 58,
        "reliability": 84,
        "headline": "타이밍은 살아났지만 기업 점수 보강이 필요한 관찰 후보",
        "reason": "가격 모멘텀은 좋지만 ROE와 밸류/퀄리티 점수가 추천 기준을 낮춥니다.",
        "warning": "플랫폼 규제와 광고 경기 변동을 확인해야 합니다.",
    },
    {
        "ticker": "068270.KS",
        "name": "셀트리온",
        "market": "KOSPI",
        "sector": "바이오",
        "industry": "바이오시밀러",
        "base_price": 189000,
        "trend": 150,
        "per": 28.4,
        "pbr": 2.5,
        "roe": 9.3,
        "eps_growth": 21.7,
        "operating_margin": 26.5,
        "debt_ratio": 46.0,
        "target_price": 218000,
        "foreign_flow": "-3.4만주",
        "institution_flow": "+9.2만주",
        "value_quality": 50,
        "annual_roe": 54,
        "eps_acceleration": 78,
        "leadership_momentum": 72,
        "pivot_breakout": 65,
        "smart_money": 68,
        "hurst": 60,
        "market_direction": 70,
        "mean_reversion": 58,
        "drawdown_control": 55,
        "reliability": 81,
        "fail_safe": True,
        "headline": "성장성은 있으나 밸류 부담과 리스크 할인이 큰 관찰 후보",
        "reason": "EPS 개선은 보이지만 가치/퀄리티와 리스크 점수가 낮습니다.",
        "warning": "신약/허가 이벤트 변동성이 커서 추격 매수는 조심해야 합니다.",
    },
    {
        "ticker": "005490.KS",
        "name": "POSCO홀딩스",
        "market": "KOSPI",
        "sector": "소재",
        "industry": "철강/2차전지 소재",
        "base_price": 411000,
        "trend": 70,
        "per": 15.2,
        "pbr": 0.63,
        "roe": 6.8,
        "eps_growth": 8.3,
        "operating_margin": 7.2,
        "debt_ratio": 67.0,
        "target_price": 465000,
        "foreign_flow": "-8.1만주",
        "institution_flow": "+3.6만주",
        "value_quality": 72,
        "annual_roe": 44,
        "eps_acceleration": 42,
        "leadership_momentum": 58,
        "pivot_breakout": 52,
        "smart_money": 56,
        "hurst": 50,
        "market_direction": 68,
        "mean_reversion": 60,
        "drawdown_control": 54,
        "reliability": 82,
        "headline": "저평가는 있으나 ROE와 모멘텀이 약한 제외 후보",
        "reason": "PBR 저평가는 좋지만 성장성과 타이밍 점수가 부족합니다.",
        "warning": "원자재 가격과 2차전지 소재 투자심리에 민감합니다.",
    },
    {
        "ticker": "035720.KS",
        "name": "카카오",
        "market": "KOSPI",
        "sector": "인터넷",
        "industry": "모바일 플랫폼",
        "base_price": 53100,
        "trend": 45,
        "per": 31.7,
        "pbr": 1.12,
        "roe": 4.4,
        "eps_growth": 6.3,
        "operating_margin": 8.7,
        "debt_ratio": 84.0,
        "target_price": 61000,
        "foreign_flow": "-11.2만주",
        "institution_flow": "-6.5만주",
        "value_quality": 45,
        "annual_roe": 34,
        "eps_acceleration": 38,
        "leadership_momentum": 52,
        "pivot_breakout": 48,
        "smart_money": 42,
        "hurst": 44,
        "market_direction": 66,
        "mean_reversion": 64,
        "drawdown_control": 48,
        "reliability": 78,
        "headline": "반등 가능성은 있지만 추천 포트폴리오에는 아직 이른 제외 후보",
        "reason": "수급과 수익성이 약해 추천 포트폴리오에는 포함하지 않습니다.",
        "warning": "규제와 사업 재편 이슈를 확인해야 합니다.",
    },
]


class Command(BaseCommand):
    help = "Seed AlphaPick stock fixtures, score reports, and daily portfolio runs."

    def add_arguments(self, parser):
        parser.add_argument("--flush", action="store_true", help="Delete existing AlphaPick stock data before seeding.")

    @transaction.atomic
    def handle(self, *args, **options):
        if options["flush"]:
            AICommentCache.objects.all().delete()
            Watchlist.objects.all().delete()
            PortfolioItem.objects.all().delete()
            PortfolioRun.objects.all().delete()
            ScoreSnapshot.objects.all().delete()
            FinancialMetric.objects.all().delete()
            PriceDaily.objects.all().delete()
            Stock.objects.all().delete()

        base_date = date.today()
        for index, item in enumerate(SAMPLE_STOCKS):
            stock, _ = Stock.objects.update_or_create(
                ticker=item["ticker"],
                defaults={
                    "name": item["name"],
                    "market": item["market"],
                    "sector": item["sector"],
                    "industry": item["industry"],
                    "primary_theme": item.get("primary_theme", item["industry"]),
                    "is_universe_included": True,
                    "low_liquidity_flag": item.get("low_liquidity", False),
                    "is_active": True,
                    "is_tradable": True,
                },
            )
            prices = self.seed_prices(stock, item, base_date, index)
            latest_close = prices[-1].close_price
            self.seed_metric(stock, item, base_date, latest_close)
            for offset in range(9, -1, -1):
                score_date = base_date - timedelta(days=offset)
                drift = -offset * 0.12
                self.seed_score(stock, item, score_date, latest_close, drift)

        for offset in range(9, -1, -1):
            ensure_portfolio_run(base_date - timedelta(days=offset))

        self.stdout.write(self.style.SUCCESS("AlphaPick sample fixtures seeded."))

    def seed_prices(self, stock, item, base_date, stock_index):
        PriceDaily.objects.filter(stock=stock).delete()
        prices = []
        closes = []
        obv = 0
        price = item["base_price"] - item["trend"] * 220
        for day in range(365):
            current_date = base_date - timedelta(days=364 - day)
            wave = sin((day + stock_index * 5) / 8) * item["base_price"] * 0.012
            price = max(1000, price + item["trend"] + wave * 0.04)
            close_price = int(price)
            open_price = int(close_price * (0.995 + (day % 5) * 0.002))
            high_price = int(max(open_price, close_price) * 1.018)
            low_price = int(min(open_price, close_price) * 0.982)
            volume = int(650000 + (stock_index + 1) * 130000 + abs(wave) * 8 + (day % 13) * 24000)
            if closes and close_price >= closes[-1]:
                obv += volume
            elif closes:
                obv -= volume
            closes.append(close_price)
            ema20 = moving_average(closes, 20)
            ema50 = moving_average(closes, 50)
            ema200 = moving_average(closes, 200)
            mean20 = moving_average(closes, 20)
            std20 = standard_deviation(closes[-20:]) if len(closes) >= 20 else 0
            prices.append(
                PriceDaily(
                    stock=stock,
                    date=current_date,
                    open_price=open_price,
                    high_price=high_price,
                    low_price=low_price,
                    close_price=close_price,
                    volume=volume,
                    ema20=round(ema20, 2),
                    ema50=round(ema50, 2),
                    ema200=round(ema200, 2),
                    bb_upper=round(mean20 + std20 * 2, 2),
                    bb_lower=round(mean20 - std20 * 2, 2),
                    obv=obv,
                )
            )
        PriceDaily.objects.bulk_create(prices)
        return prices

    def seed_metric(self, stock, item, base_date, latest_close):
        FinancialMetric.objects.update_or_create(
            stock=stock,
            base_date=base_date,
            defaults={
                "per": item["per"],
                "pbr": item["pbr"],
                "roe": item["roe"],
                "eps_growth": item["eps_growth"],
                "operating_margin": item["operating_margin"],
                "debt_ratio": item["debt_ratio"],
                "dividend_yield": 2.7 if item["sector"] == "금융" else 1.3,
                "market_cap": latest_close * 1000000,
                "target_price": item["target_price"],
                "current_price": latest_close,
                "payload": {"source": "seed_alphapick", "note": "strict 70-point recommendation fixture data"},
            },
        )

    def seed_score(self, stock, item, score_date, latest_close, drift):
        layers = score_layers(item, drift)
        total = layers["total"]
        target = clean_target_upside(item, latest_close)
        ScoreSnapshot.objects.update_or_create(
            stock=stock,
            base_date=score_date,
            defaults={
                "total_score": total,
                "company_score": layers["company"],
                "timing_score": layers["timing"],
                "reliability_score": item["reliability"],
                "financial_health_score": item["annual_roe"],
                "valuation_score": item["value_quality"],
                "growth_score": item["eps_acceleration"],
                "momentum_score": item["leadership_momentum"],
                "technical_timing_score": item["pivot_breakout"],
                "supply_score": item["smart_money"],
                "sentiment_score": item["market_direction"],
                "headline": item["headline"],
                "verdict": verdict(total),
                "signal": signal_label(total, item),
                "key_reason": key_reason(item, layers),
                "rs_rank": item["leadership_momentum"],
                "rsi": item.get("rsi", round(45 + item["leadership_momentum"] * 0.38, 1)),
                "volume_ratio": item.get("volume_ratio", 2.4 if item.get("volume_surge") else 1.2),
                "target_upside": target["upside"],
                "target_upside_clipped": target["clipped"],
                "consensus": consensus_label(total, target["upside"]),
                "confidence": confidence_label(item),
                "fail_safe_flag": item.get("fail_safe", False),
                "volume_surge_flag": item.get("volume_surge", False),
                "area_scores": {
                    "momentum": item["leadership_momentum"] - 50,
                    "value": round((item["value_quality"] - 50) / 2, 1),
                    "quality": round((item["annual_roe"] - 50) / 2, 1),
                    "risk": layers["risk_layer"],
                },
                "scoring_log": scoring_log(item, layers, target),
                "reason": item["reason"],
                "warning": item["warning"],
                "summary_metrics": summary_metrics(item, latest_close, layers),
                "timing_cards": timing_cards(item, layers),
                "score_cards": score_cards(item, layers),
                "can_slim": can_slim(item, layers),
                "technical_indicators": technical_indicators(item, layers),
                "financial_indicators": financial_indicators(item, latest_close),
                "news": news_items(item),
                "disclosures": disclosure_items(item),
            },
        )


def moving_average(values, window):
    chunk = values[-window:]
    return sum(chunk) / len(chunk)


def standard_deviation(values):
    if not values:
        return 0
    mean = sum(values) / len(values)
    return (sum((value - mean) ** 2 for value in values) / len(values)) ** 0.5


def bounded(value):
    return round(max(0, min(100, value)), 1)


def score_layers(item, drift=0):
    company = bounded(
        item["value_quality"] * 0.40
        + item["annual_roe"] * 0.30
        + item["eps_acceleration"] * 0.30
        + drift * 0.20
    )
    timing = bounded(
        item["leadership_momentum"] * 0.40
        + item["pivot_breakout"] * 0.30
        + item["smart_money"] * 0.30
        + drift * 0.40
    )
    risk_layer = bounded(
        item["market_direction"] * 0.40
        + item["mean_reversion"] * 0.30
        + item["drawdown_control"] * 0.30
        + drift * 0.10
    )
    base_score = company * 0.45 + timing * 0.55
    risk_multiplier = 0.65 + risk_layer * 0.0035
    reliability_multiplier = 0.90 + item["reliability"] * 0.001
    return {
        "company": company,
        "timing": timing,
        "risk_layer": risk_layer,
        "risk_multiplier": round(risk_multiplier, 3),
        "base_score": round(base_score, 1),
        "total": bounded(base_score * risk_multiplier * reliability_multiplier),
    }


def verdict(score):
    if score >= 85:
        return "핵심 추천"
    if score >= 70:
        return "추천 후보"
    if score >= 60:
        return "관찰 후보"
    return "제외"


def clean_target_upside(item, latest_close):
    raw = item.get("target_upside_raw")
    if raw is None:
        raw = ((item["target_price"] - latest_close) / latest_close * 100) if latest_close else None
    if raw is None:
        return {"upside": None, "clipped": False}
    clipped = max(-99, min(200, float(raw)))
    return {"upside": round(clipped, 1), "clipped": clipped != float(raw)}


def signal_label(score, item):
    tags = []
    if item["pivot_breakout"] >= 75:
        tags.append("[PIVOT]")
    if item["eps_acceleration"] >= 80:
        tags.append("[EPS]")
    if item["hurst"] >= 60:
        tags.append("[TREND]")
    if item.get("volume_surge"):
        tags.append("[VOL]")
    if item.get("low_liquidity"):
        tags.append("[LOW LIQ]")
    if item.get("fail_safe"):
        tags.append("[FAIL-SAFE]")

    if score >= 85:
        prefix = "STRONG LEADER"
    elif score >= 70:
        prefix = "LEADER"
    elif score >= 60:
        prefix = "WATCH LIST"
    elif score >= 45:
        prefix = "CAUTION"
    else:
        prefix = "AVOID"
    suffix = " ".join(tags)
    return f"{prefix} {suffix}".strip()


def key_reason(item, layers):
    parts = []
    if item["pivot_breakout"] >= 75:
        parts.append("52주 신고가 근접")
    if item["leadership_momentum"] >= 75:
        parts.append(f"RS {item['leadership_momentum']}")
    if item["eps_acceleration"] >= 70:
        parts.append("EPS 가속")
    if item["annual_roe"] >= 70:
        parts.append(f"ROE {item['roe']}%")
    if not parts:
        parts.append(f"리스크 할인 x{layers['risk_multiplier']}")
    return " · ".join(parts)


def consensus_label(score, target_upside):
    if target_upside is not None and target_upside < 0:
        return "OVERVALUED"
    if score >= 80:
        return "STRONG_BUY"
    if score >= 70:
        return "BUY"
    if score >= 60:
        return "WATCH"
    return "NEUTRAL"


def confidence_label(item):
    if item["reliability"] >= 90:
        return "HIGH"
    if item["reliability"] >= 80:
        return "MID"
    return "LOW"


def scoring_log(item, layers, target):
    logs = [
        f"기업 점수 {layers['company']}점: 가치/퀄리티 {item['value_quality']} + ROE {item['annual_roe']} + EPS {item['eps_acceleration']}",
        f"타이밍 점수 {layers['timing']}점: 모멘텀 {item['leadership_momentum']} + 피벗 {item['pivot_breakout']} + 수급 {item['smart_money']}",
        f"리스크 할인 x{layers['risk_multiplier']}: 시장 {item['market_direction']} / 과열 {item['mean_reversion']} / 낙폭 {item['drawdown_control']}",
    ]
    if target["clipped"]:
        logs.append("목표가 상승여력 이상치가 감지되어 +200%로 클리핑했습니다.")
    if item.get("low_liquidity"):
        logs.append("LOW LIQ 플래그로 추천 포트폴리오 편입에서 제외합니다.")
    if item.get("fail_safe"):
        logs.append("Fail-safe 플래그로 추천 포트폴리오 편입에서 제외합니다.")
    if item.get("volume_surge"):
        logs.append("거래량 급증 플래그가 감지되었습니다.")
    return logs


def status_for(score):
    if score >= 80:
        return "good"
    if score >= 60:
        return "neutral"
    return "bad"


def summary_metrics(item, latest_close, layers):
    return [
        f"현재가 {latest_close:,}원",
        f"총점 {layers['total']}점",
        f"기업 {layers['company']}점",
        f"타이밍 {layers['timing']}점",
        f"리스크 할인 x{layers['risk_multiplier']}",
    ]


def timing_cards(item, layers):
    return [
        {
            "label": "기업 점수",
            "score": round(layers["company"] / 20, 1),
            "max": 5,
            "description": "가치/퀄리티, 연간 ROE, EPS 가속도를 40:30:30으로 합산합니다.",
        },
        {
            "label": "타이밍 점수",
            "score": round(layers["timing"] / 20, 1),
            "max": 5,
            "description": "주도주 모멘텀, 피벗 돌파, 스마트머니 수급을 40:30:30으로 합산합니다.",
        },
        {
            "label": "리스크 안전도",
            "score": round(layers["risk_layer"] / 20, 1),
            "max": 5,
            "description": "시장 방향, 단기 과열, 낙폭 위험도를 점수 할인 계수로 반영합니다.",
        },
        {
            "label": "데이터 신뢰도",
            "score": round(item["reliability"] / 20, 1),
            "max": 5,
            "description": "가격/재무/기술 지표 결측과 거래 가능 여부를 반영합니다.",
        },
    ]


def score_cards(item, layers):
    return [
        card("Q", "company", "가치/퀄리티 팩터", f"PER {item['per']} · PBR {item['pbr']}", item["value_quality"], "내재 가치와 현재 주가의 괴리를 평가합니다."),
        card("A", "company", "연간 ROE 실적", f"ROE {item['roe']}%", item["annual_roe"], "CAN SLIM의 A. 자본 대비 이익 창출력을 봅니다."),
        card("C", "company", "EPS 가속도", f"EPS 성장률 {item['eps_growth']}%", item["eps_acceleration"], "CAN SLIM의 C. 최근 이익 성장세가 가파른지 확인합니다."),
        card("L", "timing", "주도주 판별 & 모멘텀", "RS/3M/12M 통합", item["leadership_momentum"], "가격의 상대적 강도와 다중 시간대 모멘텀을 하나로 묶었습니다."),
        card("N", "timing", "신고가/피벗 돌파", "칼만 필터 기준 돌파", item["pivot_breakout"], "노이즈 제거 가격선을 기준으로 핵심 진입 신호를 평가합니다."),
        card("I", "timing", "스마트머니 & 기관 수급", f"외국인 {item['foreign_flow']} · 기관 {item['institution_flow']}", item["smart_money"], "거래량 돌파, 기관 수급, 큰 손의 매수세를 통합합니다."),
        card("H", "preprocess", "허스트 지수", "추세성 전처리", item["hurst"], "최종 점수에 직접 더하지 않고 모멘텀 가중치 조절용으로만 사용합니다."),
        card("M", "risk", "시장 방향 (M)", "KOSPI/KOSDAQ 방향", item["market_direction"], "시장 방향이 꺾이면 개별 종목 점수도 할인합니다."),
        card("Z", "risk", "평균 회귀 (Z-Score)", "단기 과열 경고", item["mean_reversion"], "추세 추종 모델에서 과열 추격 매수를 막는 경고등입니다."),
        card("D", "risk", "낙폭 위험도", "MDD/변동성/공매도 통합", item["drawdown_control"], "하방 위험이 높을수록 최종 총점을 할인합니다."),
    ]


def card(code, group, title, raw_value, score, reason):
    return {
        "code": code,
        "group": group,
        "title": title,
        "rawValue": raw_value,
        "score": round(score, 1),
        "status": status_for(score),
        "reason": reason,
    }


def can_slim(item, layers):
    return [
        {"code": "C", "label": "Current EPS", "status": "pass" if item["eps_acceleration"] >= 70 else "watch", "reason": f"EPS 가속도 {item['eps_acceleration']}점"},
        {"code": "A", "label": "Annual Earnings", "status": "pass" if item["annual_roe"] >= 70 else "watch", "reason": f"연간 ROE 실적 {item['annual_roe']}점"},
        {"code": "N", "label": "New High", "status": "pass" if item["pivot_breakout"] >= 75 else "watch", "reason": f"신고가/피벗 돌파 {item['pivot_breakout']}점"},
        {"code": "S", "label": "Supply", "status": "pass" if item["smart_money"] >= 70 else "watch", "reason": f"스마트머니 수급 {item['smart_money']}점"},
        {"code": "L", "label": "Leader", "status": "pass" if item["leadership_momentum"] >= 80 else "watch", "reason": f"주도주 모멘텀 {item['leadership_momentum']}점"},
        {"code": "I", "label": "Institution", "status": "pass" if item["institution_flow"].startswith("+") else "watch", "reason": f"기관 {item['institution_flow']}"},
        {"code": "M", "label": "Market", "status": "pass" if item["market_direction"] >= 75 else "watch", "reason": f"시장 방향 {item['market_direction']}점"},
    ]


def technical_indicators(item, layers):
    return [
        {"name": "RS 등급", "value": str(item["leadership_momentum"]), "status": "주도주" if item["leadership_momentum"] >= 80 else "중립", "description": "80 이상이면 시장 대비 상대강도가 강하다고 봅니다."},
        {"name": "신고가/피벗", "value": str(item["pivot_breakout"]), "status": "돌파권" if item["pivot_breakout"] >= 75 else "대기", "description": "칼만 필터로 노이즈를 줄인 가격선 기준 돌파 점수입니다."},
        {"name": "Z-Score 과열", "value": str(item["mean_reversion"]), "status": "양호" if item["mean_reversion"] >= 70 else "주의", "description": "높을수록 단기 과열 부담이 낮다는 뜻입니다."},
        {"name": "허스트 지수", "value": str(item["hurst"]), "status": "추세적" if item["hurst"] >= 60 else "랜덤워크", "description": "최종 점수에는 직접 더하지 않는 모멘텀 전처리 지표입니다."},
        {"name": "리스크 할인", "value": f"x{layers['risk_multiplier']}", "status": "할인 반영", "description": "시장 방향, 과열, 낙폭 위험을 합쳐 총점에 곱합니다."},
    ]


def financial_indicators(item, latest_close):
    target = clean_target_upside(item, latest_close)
    upside_value = "목표가 미산정" if target["upside"] is None else f"{target['upside']}%"
    target_status = "200%+ 클리핑" if target["clipped"] else "차트 보조선"
    return [
        {"name": "PER", "value": f"{item['per']}배", "status": "저평가 가능" if item["per"] <= 15 else "부담", "description": "낮을수록 이익 대비 가격 부담이 작습니다."},
        {"name": "PBR", "value": f"{item['pbr']}배", "status": "자산 대비 저평가" if item["pbr"] <= 1 else "중립", "description": "1 이하이면 자산 대비 저평가 가능성이 있습니다."},
        {"name": "ROE", "value": f"{item['roe']}%", "status": "양호" if item["roe"] >= 10 else "보통", "description": "자기자본 대비 이익 창출력입니다."},
        {"name": "EPS 성장률", "value": f"+{item['eps_growth']}%", "status": "성장" if item["eps_growth"] >= 15 else "둔화", "description": "전년 대비 이익 성장률입니다."},
        {"name": "부채비율", "value": f"{item['debt_ratio']}%", "status": "주의" if item["debt_ratio"] > 200 else "양호", "description": "업종별 차이가 커서 섹터 맥락과 함께 봅니다."},
        {"name": "Target Price Factor", "value": upside_value, "status": target_status, "description": "최종 점수에서는 제외하고 참고용 보조선과 경고 배지로만 사용합니다."},
    ]


def news_items(item):
    return [
        {"title": f"{item['name']}, 실적 개선 기대감 점검", "sentiment": "positive", "source": "MVP 뉴스", "publishedAt": "2026-05-22"},
        {"title": f"{item['name']} 수급 흐름 재평가 필요", "sentiment": "neutral", "source": "MVP 뉴스", "publishedAt": "2026-05-21"},
        {"title": f"{item['sector']} 업종 투자심리 회복", "sentiment": "positive", "source": "MVP 뉴스", "publishedAt": "2026-05-20"},
    ]


def disclosure_items(item):
    return [
        {"title": "분기보고서", "date": "2026-05-15"},
        {"title": "기업설명회(IR) 개최", "date": "2026-05-10"},
        {"title": "주요사항보고서", "date": "2026-05-03"},
    ]

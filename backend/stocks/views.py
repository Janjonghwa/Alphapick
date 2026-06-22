from datetime import date

from django.db.models import Q
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Stock, Watchlist
from .serializers import AICommentSerializer, PortfolioSerializer, PriceDailySerializer, StockReportSerializer, StockSummarySerializer
from .services import (
    PRICE_HISTORY_DAYS,
    build_dynamic_portfolio_payload,
    calculate_backtest,
    generate_ai_comment,
    latest_score_date,
    normalize_risk_type,
    portfolio_history,
    stock_report,
)


class StockViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = StockSummarySerializer
    lookup_field = "ticker"
    lookup_value_regex = r"[^/]+"
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        score_date = latest_score_date()
        queryset = Stock.objects.filter(is_active=True).prefetch_related("scores", "financial_metrics")
        query = self.request.query_params.get("q")
        sector = self.request.query_params.get("sector")
        market = self.request.query_params.get("market")
        min_score = self.request.query_params.get("min_score")

        if query:
            queryset = queryset.filter(Q(name__icontains=query) | Q(ticker__icontains=query))
        if sector:
            queryset = queryset.filter(sector=sector)
        if market:
            queryset = queryset.filter(market=market)
        if score_date:
            queryset = queryset.filter(scores__base_date=score_date)
        if min_score:
            queryset = queryset.filter(scores__total_score__gte=float(min_score)).distinct()
        return queryset.order_by("-scores__total_score", "name").distinct()

    @action(detail=True, methods=["get"], url_path="report")
    def report(self, request, ticker=None):
        data = stock_report(ticker)
        return Response(StockReportSerializer(data).data)

    @action(detail=True, methods=["get"], url_path="prices")
    def prices(self, request, ticker=None):
        stock = self.get_object()
        prices = stock.prices.order_by("-date")[: int(request.query_params.get("limit", PRICE_HISTORY_DAYS))]
        return Response(PriceDailySerializer(reversed(list(prices)), many=True).data)

    @action(detail=True, methods=["post"], url_path="ai-comment")
    def ai_comment(self, request, ticker=None):
        risk_type = normalize_risk_type(request.data.get("risk_type") or request.query_params.get("risk_type"))
        try:
            comment, cached = generate_ai_comment(ticker, risk_type=risk_type)
        except ValueError:
            return Response({"detail": "아직 생성 가능한 스코어 리포트가 없습니다."}, status=status.HTTP_404_NOT_FOUND)
        return Response({**AICommentSerializer(comment).data, "cached": cached})


class TodayPortfolioView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        if latest_score_date() is None:
            return Response(
                {
                    "detail": "아직 로드된 주식 데이터가 없습니다. python manage.py seed_alphapick 명령으로 샘플 fixtures를 적재하세요.",
                    "items": [],
                    "watchCandidates": [],
                },
                status=status.HTTP_200_OK,
            )
        risk_type = normalize_risk_type(request.query_params.get("risk_type"))
        return Response(build_dynamic_portfolio_payload(risk_type=risk_type))


class PortfolioHistoryView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        limit = int(request.query_params.get("limit", 20))
        return Response(PortfolioSerializer(portfolio_history(limit), many=True).data)


class PortfolioBacktestView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        benchmark = request.query_params.get("benchmark", "KOSPI")
        period = request.query_params.get("period", "1y")
        risk_type = normalize_risk_type(request.query_params.get("risk_type"))
        return Response(calculate_backtest(benchmark=benchmark, period=period, risk_type=risk_type))


class MarketMacroView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response(
            {
                "asOf": date.today().isoformat(),
                "sentiment": {
                    "score": 42,
                    "label": "공포",
                    "level": "fear",
                    "summary": "변동성은 완화됐지만 지수 모멘텀은 아직 방어적입니다.",
                },
                "items": [
                    {"key": "vix", "label": "VIX", "value": 16.40, "change": -11.06, "unit": "%", "invert": True},
                    {"key": "sp500", "label": "S&P500", "value": 7500.58, "change": 1.08, "unit": "%"},
                    {"key": "nasdaq", "label": "나스닥", "value": 26517.93, "change": 1.91, "unit": "%"},
                    {"key": "kospi", "label": "KOSPI", "value": 9147.24, "change": 1.05, "unit": "%"},
                    {"key": "usdkrw", "label": "원/달러", "value": 1538.8, "change": 0.08, "unit": "%"},
                    {"key": "dxy", "label": "DXY", "value": 100.86, "change": 0.01, "unit": "%"},
                    {"key": "us10y", "label": "美10Y", "value": 4.45, "change": -0.27, "unit": "%", "valueSuffix": "%"},
                    {"key": "gold", "label": "금", "value": 4172.9, "change": -1.21, "unit": "%"},
                    {"key": "wti", "label": "WTI", "value": 75.53, "change": -1.40, "unit": "%"},
                    {"key": "btc", "label": "BTC", "value": 64448, "change": 0.32, "unit": "%"},
                    {"key": "us_rate", "label": "美기준금리", "value": 3.75, "valueSuffix": "%"},
                    {"key": "kr_rate", "label": "韓기준금리", "value": 2.50, "valueSuffix": "%"},
                ],
                "source": "데모 fallback 데이터",
                "updatedAgo": "14분 전 갱신",
            }
        )


class MarketEventsView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        today = date.today()
        events = [
            {"kind": "nfp", "label": "고용", "name": "고용보고서 (6월)", "date": "2026-07-03"},
            {"kind": "cpi", "label": "CPI", "name": "CPI (6월)", "date": "2026-07-14"},
            {"kind": "fomc", "label": "FOMC", "name": "FOMC 회의", "date": "2026-07-29"},
            {"kind": "nfp", "label": "고용", "name": "고용보고서 (7월)", "date": "2026-08-07"},
            {"kind": "cpi", "label": "CPI", "name": "CPI (7월)", "date": "2026-08-12"},
        ]
        for event in events:
            event_date = date.fromisoformat(event["date"])
            event["dday"] = (event_date - today).days
        return Response({"asOf": today.isoformat(), "events": events})


class WatchlistView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, ticker):
        stock = generics.get_object_or_404(Stock, ticker=ticker)
        Watchlist.objects.get_or_create(user=request.user, stock=stock)
        return Response({"ticker": ticker, "saved": True}, status=status.HTTP_201_CREATED)

    def delete(self, request, ticker):
        Watchlist.objects.filter(user=request.user, stock_id=ticker).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MyWatchlistView(generics.ListAPIView):
    serializer_class = StockSummarySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Stock.objects.filter(watchlisted_by__user=self.request.user).prefetch_related("scores", "financial_metrics")

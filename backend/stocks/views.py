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
        return Response(calculate_backtest(benchmark=benchmark))


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

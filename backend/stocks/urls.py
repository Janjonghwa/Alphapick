from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    MarketEventsView,
    MarketMacroView,
    MyWatchlistView,
    PortfolioBacktestView,
    PortfolioHistoryView,
    StockViewSet,
    TodayPortfolioView,
    WatchlistView,
)


router = DefaultRouter()
router.register("stocks", StockViewSet, basename="stock")

urlpatterns = [
    path("portfolio/today/", TodayPortfolioView.as_view(), name="portfolio-today"),
    path("portfolio/history/", PortfolioHistoryView.as_view(), name="portfolio-history"),
    path("portfolio/backtest/", PortfolioBacktestView.as_view(), name="portfolio-backtest"),
    path("market/macro/", MarketMacroView.as_view(), name="market-macro"),
    path("market/events/", MarketEventsView.as_view(), name="market-events"),
    path("watchlist/", MyWatchlistView.as_view(), name="watchlist"),
    path("watchlist/<str:ticker>/", WatchlistView.as_view(), name="watchlist-toggle"),
    path("", include(router.urls)),
]

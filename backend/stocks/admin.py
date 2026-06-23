from django.contrib import admin

from .models import (
    AICommentCache,
    FinancialMetric,
    PortfolioItem,
    PortfolioRun,
    PriceDaily,
    ScoreSnapshot,
    Stock,
    StockTheme,
    Theme,
    ThemeGroup,
    Watchlist,
)


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ("ticker", "name", "market", "sector", "is_active", "is_tradable")
    list_filter = ("market", "sector", "is_active", "is_tradable")
    search_fields = ("ticker", "name")


@admin.register(ScoreSnapshot)
class ScoreSnapshotAdmin(admin.ModelAdmin):
    list_display = ("stock", "base_date", "total_score", "company_score", "timing_score", "reliability_score")
    list_filter = ("base_date", "verdict")
    search_fields = ("stock__ticker", "stock__name")


@admin.register(PortfolioRun)
class PortfolioRunAdmin(admin.ModelAdmin):
    list_display = ("base_date", "threshold", "rebalance_type", "portfolio_score")


admin.site.register(PriceDaily)
admin.site.register(FinancialMetric)
admin.site.register(PortfolioItem)
admin.site.register(ThemeGroup)
admin.site.register(Theme)
admin.site.register(StockTheme)
admin.site.register(Watchlist)
admin.site.register(AICommentCache)

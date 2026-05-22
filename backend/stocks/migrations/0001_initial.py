# Generated manually for the AlphaPick MVP.

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="PortfolioRun",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("base_date", models.DateField(db_index=True, unique=True)),
                ("threshold", models.FloatField(default=95)),
                ("rebalance_type", models.CharField(default="daily", max_length=20)),
                ("portfolio_score", models.FloatField(default=0)),
                ("summary", models.TextField(blank=True)),
                ("sector_warning", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "ordering": ("-base_date",),
            },
        ),
        migrations.CreateModel(
            name="Stock",
            fields=[
                ("ticker", models.CharField(max_length=20, primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=120)),
                ("market", models.CharField(db_index=True, max_length=20)),
                ("sector", models.CharField(db_index=True, max_length=80)),
                ("industry", models.CharField(blank=True, max_length=120)),
                ("is_active", models.BooleanField(default=True)),
                ("is_tradable", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "ordering": ("ticker",),
            },
        ),
        migrations.CreateModel(
            name="FinancialMetric",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("base_date", models.DateField(db_index=True)),
                ("per", models.FloatField(blank=True, null=True)),
                ("pbr", models.FloatField(blank=True, null=True)),
                ("roe", models.FloatField(blank=True, null=True)),
                ("eps_growth", models.FloatField(blank=True, null=True)),
                ("operating_margin", models.FloatField(blank=True, null=True)),
                ("debt_ratio", models.FloatField(blank=True, null=True)),
                ("dividend_yield", models.FloatField(blank=True, null=True)),
                ("market_cap", models.FloatField(blank=True, null=True)),
                ("target_price", models.PositiveIntegerField(blank=True, null=True)),
                ("current_price", models.PositiveIntegerField(blank=True, null=True)),
                ("payload", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("stock", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="financial_metrics", to="stocks.stock")),
            ],
            options={
                "ordering": ("-base_date",),
            },
        ),
        migrations.CreateModel(
            name="PriceDaily",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("date", models.DateField(db_index=True)),
                ("open_price", models.PositiveIntegerField()),
                ("high_price", models.PositiveIntegerField()),
                ("low_price", models.PositiveIntegerField()),
                ("close_price", models.PositiveIntegerField()),
                ("volume", models.PositiveIntegerField()),
                ("ema20", models.FloatField(blank=True, null=True)),
                ("ema50", models.FloatField(blank=True, null=True)),
                ("ema200", models.FloatField(blank=True, null=True)),
                ("bb_upper", models.FloatField(blank=True, null=True)),
                ("bb_lower", models.FloatField(blank=True, null=True)),
                ("obv", models.FloatField(blank=True, null=True)),
                ("stock", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="prices", to="stocks.stock")),
            ],
            options={
                "ordering": ("date",),
            },
        ),
        migrations.CreateModel(
            name="ScoreSnapshot",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("base_date", models.DateField(db_index=True)),
                ("total_score", models.FloatField(db_index=True)),
                ("company_score", models.FloatField()),
                ("timing_score", models.FloatField()),
                ("reliability_score", models.FloatField()),
                ("financial_health_score", models.FloatField(default=0)),
                ("valuation_score", models.FloatField(default=0)),
                ("growth_score", models.FloatField(default=0)),
                ("momentum_score", models.FloatField(default=0)),
                ("technical_timing_score", models.FloatField(default=0)),
                ("supply_score", models.FloatField(default=0)),
                ("sentiment_score", models.FloatField(default=0)),
                ("headline", models.CharField(max_length=180)),
                ("verdict", models.CharField(max_length=40)),
                ("reason", models.TextField()),
                ("warning", models.TextField(blank=True)),
                ("summary_metrics", models.JSONField(blank=True, default=list)),
                ("timing_cards", models.JSONField(blank=True, default=list)),
                ("score_cards", models.JSONField(blank=True, default=list)),
                ("can_slim", models.JSONField(blank=True, default=list)),
                ("technical_indicators", models.JSONField(blank=True, default=list)),
                ("financial_indicators", models.JSONField(blank=True, default=list)),
                ("news", models.JSONField(blank=True, default=list)),
                ("disclosures", models.JSONField(blank=True, default=list)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("stock", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="scores", to="stocks.stock")),
            ],
            options={
                "ordering": ("-base_date", "-total_score"),
            },
        ),
        migrations.CreateModel(
            name="PortfolioItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("score", models.FloatField()),
                ("weight", models.FloatField()),
                ("reason", models.TextField()),
                ("warning", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("portfolio_run", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="items", to="stocks.portfoliorun")),
                ("score_snapshot", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="portfolio_items", to="stocks.scoresnapshot")),
                ("stock", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="portfolio_items", to="stocks.stock")),
            ],
            options={
                "ordering": ("-score", "stock_id"),
            },
        ),
        migrations.CreateModel(
            name="Watchlist",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("stock", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="watchlisted_by", to="stocks.stock")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="stock_watchlist", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ("-created_at",),
            },
        ),
        migrations.AddIndex(
            model_name="stock",
            index=models.Index(fields=["market", "sector"], name="stocks_stoc_market_f50b95_idx"),
        ),
        migrations.AddIndex(
            model_name="stock",
            index=models.Index(fields=["name"], name="stocks_stoc_name_6f3be2_idx"),
        ),
        migrations.AddConstraint(
            model_name="financialmetric",
            constraint=models.UniqueConstraint(fields=("stock", "base_date"), name="unique_stock_metric_date"),
        ),
        migrations.AddConstraint(
            model_name="pricedaily",
            constraint=models.UniqueConstraint(fields=("stock", "date"), name="unique_stock_price_date"),
        ),
        migrations.AddConstraint(
            model_name="scoresnapshot",
            constraint=models.UniqueConstraint(fields=("stock", "base_date"), name="unique_stock_score_date"),
        ),
        migrations.AddConstraint(
            model_name="portfolioitem",
            constraint=models.UniqueConstraint(fields=("portfolio_run", "stock"), name="unique_portfolio_stock"),
        ),
        migrations.AddConstraint(
            model_name="watchlist",
            constraint=models.UniqueConstraint(fields=("user", "stock"), name="unique_user_stock_watchlist"),
        ),
    ]

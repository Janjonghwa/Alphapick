# Generated manually for AlphaPick AI comment cache.

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("stocks", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="AICommentCache",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("base_date", models.DateField(db_index=True)),
                (
                    "risk_type",
                    models.CharField(
                        choices=[("aggressive", "Aggressive"), ("neutral", "Neutral"), ("stable", "Stable")],
                        default="neutral",
                        max_length=20,
                    ),
                ),
                ("positive", models.TextField()),
                ("negative", models.TextField()),
                ("conclusion", models.TextField()),
                ("provider", models.CharField(default="local-mvp", max_length=40)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("stock", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="ai_comments", to="stocks.stock")),
            ],
            options={
                "ordering": ("-base_date", "stock_id"),
            },
        ),
        migrations.AddConstraint(
            model_name="aicommentcache",
            constraint=models.UniqueConstraint(fields=("stock", "base_date", "risk_type"), name="unique_ai_comment_stock_date_risk"),
        ),
    ]

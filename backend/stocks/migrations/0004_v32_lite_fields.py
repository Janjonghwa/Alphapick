# Generated manually for AlphaPick v3.2 Lite data-validation fields.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("stocks", "0003_alter_portfoliorun_threshold"),
    ]

    operations = [
        migrations.AddField(
            model_name="stock",
            name="primary_theme",
            field=models.CharField(blank=True, db_index=True, max_length=80),
        ),
        migrations.AddField(
            model_name="stock",
            name="is_universe_included",
            field=models.BooleanField(db_index=True, default=True),
        ),
        migrations.AddField(
            model_name="stock",
            name="low_liquidity_flag",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="scoresnapshot",
            name="signal",
            field=models.CharField(blank=True, max_length=160),
        ),
        migrations.AddField(
            model_name="scoresnapshot",
            name="key_reason",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="scoresnapshot",
            name="rs_rank",
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="scoresnapshot",
            name="rsi",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="scoresnapshot",
            name="volume_ratio",
            field=models.FloatField(default=1.0),
        ),
        migrations.AddField(
            model_name="scoresnapshot",
            name="target_upside",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="scoresnapshot",
            name="target_upside_clipped",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="scoresnapshot",
            name="consensus",
            field=models.CharField(blank=True, max_length=40),
        ),
        migrations.AddField(
            model_name="scoresnapshot",
            name="confidence",
            field=models.CharField(blank=True, max_length=10),
        ),
        migrations.AddField(
            model_name="scoresnapshot",
            name="fail_safe_flag",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="scoresnapshot",
            name="volume_surge_flag",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="scoresnapshot",
            name="area_scores",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name="scoresnapshot",
            name="scoring_log",
            field=models.JSONField(blank=True, default=list),
        ),
    ]

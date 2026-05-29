from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="risk_type",
            field=models.CharField(
                choices=[
                    ("aggressive", "Aggressive"),
                    ("neutral", "Neutral"),
                    ("stable", "Stable"),
                ],
                default="neutral",
                max_length=20,
            ),
        ),
        migrations.RemoveField(
            model_name="user",
            name="level",
        ),
        migrations.RemoveField(
            model_name="user",
            name="preferred_location",
        ),
        migrations.RemoveField(
            model_name="user",
            name="preferred_categories",
        ),
        migrations.RemoveField(
            model_name="user",
            name="onboarding_completed",
        ),
    ]

# Generated manually for AlphaPick 70-point recommendation policy.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("stocks", "0002_aicommentcache"),
    ]

    operations = [
        migrations.AlterField(
            model_name="portfoliorun",
            name="threshold",
            field=models.FloatField(default=70),
        ),
    ]

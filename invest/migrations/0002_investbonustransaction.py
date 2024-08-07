# Generated by Django 4.2.2 on 2023-07-25 06:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("invest", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="InvestBonusTransaction",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("amount", models.FloatField()),
                ("rate", models.FloatField()),
                ("bonus", models.FloatField()),
                (
                    "status",
                    models.IntegerField(
                        choices=[(1, "pending"), (2, "authorized"), (3, "voided")],
                        default=1,
                    ),
                ),
                ("date_created", models.DateTimeField(auto_now_add=True, null=True)),
                (
                    "invest",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="invest_bonus_transactions",
                        to="invest.invest",
                    ),
                ),
            ],
            options={
                "db_table": "invest_bonus_transaction",
            },
        ),
    ]

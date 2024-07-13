# Generated by Django 4.2.1 on 2023-06-13 12:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("contract", "0004_rename_term_rate_limit_contract_limit_rate"),
        ("stake", "0002_stake_available_amount"),
    ]

    operations = [
        migrations.CreateModel(
            name="Invest",
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
                ("invest_date", models.DateTimeField(auto_now_add=True)),
                (
                    "invest_status",
                    models.IntegerField(
                        choices=[(1, "active"), (2, "suspended")], default=1
                    ),
                ),
                (
                    "contract",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="invests",
                        to="contract.contract",
                    ),
                ),
                (
                    "stake",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="invests",
                        to="stake.stake",
                    ),
                ),
            ],
            options={
                "db_table": "invest",
            },
        ),
    ]

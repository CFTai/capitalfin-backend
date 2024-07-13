# Generated by Django 4.2.1 on 2023-06-12 02:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("term", "0002_term"),
    ]

    operations = [
        migrations.CreateModel(
            name="Contract",
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
                ("title", models.CharField(max_length=255)),
                ("term_rate_limit", models.FloatField(default=0)),
                ("roi_rate", models.FloatField(default=0)),
                ("contract_value", models.FloatField(default=0)),
                ("invested_value", models.FloatField(default=0)),
                ("investment_start", models.DateTimeField(null=True)),
                ("investment_end", models.DateTimeField(null=True)),
                ("process_end", models.DateTimeField(null=True)),
                ("date_created", models.DateTimeField(auto_now_add=True)),
                ("date_updated", models.DateTimeField(auto_now=True)),
                (
                    "contract_status",
                    models.IntegerField(
                        choices=[
                            (1, "inactive"),
                            (2, "open"),
                            (3, "closed"),
                            (4, "processing"),
                            (5, "completed"),
                            (6, "suspended"),
                        ],
                        default=1,
                    ),
                ),
                (
                    "term",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="contracts",
                        to="term.term",
                    ),
                ),
            ],
            options={
                "db_table": "contract",
            },
        ),
    ]

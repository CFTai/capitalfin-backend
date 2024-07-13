# Generated by Django 5.0.6 on 2024-06-30 06:26

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("invest", "0005_alter_invest_options_and_more"),
        ("stake", "0003_alter_stake_options"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="invest",
            name="invest_date",
        ),
        migrations.RemoveField(
            model_name="invest",
            name="invest_status",
        ),
        migrations.AddField(
            model_name="invest",
            name="bonus_income_cap",
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name="invest",
            name="end_date",
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name="invest",
            name="shares_amount",
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name="invest",
            name="start_date",
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name="invest",
            name="status",
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name="invest",
            name="total_amount",
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name="invest",
            name="stake",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="invests",
                to="stake.stake",
            ),
        ),
    ]
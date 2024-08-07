# Generated by Django 5.0.6 on 2024-06-30 06:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("transaction", "0004_alter_transaction_options"),
    ]

    operations = [
        migrations.AlterField(
            model_name="transaction",
            name="transaction_type",
            field=models.IntegerField(
                choices=[
                    (1, "admin_transaction"),
                    (2, "transfer_transaction"),
                    (3, "transfer_fee"),
                    (4, "withdrawal_transaction"),
                    (5, "withdrawal_fee"),
                    (6, "deposit_transaction"),
                    (7, "shares_transaction"),
                    (8, "sponsor_bonus"),
                    (9, "trading_bonus"),
                    (10, "tiering_bonus"),
                    (11, "stake_purchase_transaction"),
                    (12, "stake_topup_transaction"),
                    (13, "stake_upgrade_transaction"),
                    (14, "invest_transaction"),
                    (15, "invest_topup_transaction"),
                ]
            ),
        ),
    ]

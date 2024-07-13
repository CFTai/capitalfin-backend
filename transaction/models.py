from django.db import models


# Create your models here.
class Transaction(models.Model):
    AUTHORIZED = 1
    VOIDED = 2
    PENDING = 3
    TRANSACTION_STATUS = [
        (1, "authorized"),
        (2, "voided"),
        (3, "pending"),
    ]

    ADMIN_TRANSACTION = 1
    TRANSFER_TRANSACTION = 2
    TRANSFER_FEE = 3
    WITHDRAWAL_TRANSACTION = 4
    WITHDRAWAL_FEE = 5
    DEPOSIT_TRANSACTION = 6
    SHARES_TRANSACTION = 7
    SPONSOR_BONUS = 8
    TRADING_BONUS = 9
    TIERING_BONUS = 10
    STAKE_PURCHASE_TRANSACTION = 11
    STAKE_TOPUP_TRANSACTION = 12
    STAKE_UPGRADE_TRANSACTION = 13
    INVEST_TRANSACTION = 14
    INVEST_TOPUP_TRANSACTION = 15
    TRANSACTION_TYPES = [
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

    amount = models.FloatField()
    remark = models.TextField(null=True, blank=True)
    transaction_type = models.IntegerField(choices=TRANSACTION_TYPES)
    transaction_status = models.IntegerField(
        choices=TRANSACTION_STATUS, default=AUTHORIZED
    )
    transaction_date = models.DateTimeField(auto_now_add=True)
    account = models.ForeignKey(
        "account.Account", on_delete=models.CASCADE, related_name="transactions"
    )

    class Meta:
        db_table = "transaction"
        ordering = ["id"]

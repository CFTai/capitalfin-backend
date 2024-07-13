from django.db import models


# Create your models here.
class Invest(models.Model):
    ACTIVE = 1
    SUSPENDED = 2
    COMPLETED = 3
    PAID = 4
    INVEST_STATUS = [
        (1, "active"),
        (2, "suspended"),
        (3, "completed"),
        (4, "paid"),
    ]

    amount = models.FloatField()
    shares_amount = models.FloatField(default=0)
    total_amount = models.FloatField(default=0)
    bonus_income_cap = models.FloatField(default=0)
    bonus_total_payout = models.FloatField(default=0)
    start_date = models.DateTimeField(null=True)
    end_date = models.DateTimeField(null=True)
    status = models.IntegerField(default=ACTIVE, choices=INVEST_STATUS)
    contract = models.ForeignKey(
        "contract.Contract", on_delete=models.CASCADE, related_name="invests"
    )
    stake = models.ForeignKey(
        "stake.Stake", on_delete=models.CASCADE, related_name="invests", null=True
    )

    class Meta:
        db_table = "invest"
        ordering = ["id"]


class InvestBonusTransaction(models.Model):
    PENDING = 1
    AUTHORIZED = 2
    VOIDED = 3
    PROCESSING = 4

    STATUS = [
        (1, "pending"),
        (2, "authorized"),
        (3, "voided"),
        (4, "processing"),
    ]

    amount = models.FloatField()
    rate = models.FloatField()
    bonus = models.FloatField()
    status = models.IntegerField(choices=STATUS, default=PROCESSING)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    invest = models.ForeignKey(
        Invest, on_delete=models.CASCADE, related_name="invest_bonus_transactions"
    )

    class Meta:
        db_table = "invest_bonus_transaction"
        ordering = ["id"]

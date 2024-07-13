from django.db import models


# Create your models here.
class GoldmineBonusSettings(models.Model):
    rate = models.FloatField()
    max_level = models.IntegerField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    term = models.ForeignKey(
        "term.Term", on_delete=models.CASCADE, related_name="goldmine_bonus_settings"
    )

    class Meta:
        db_table = "goldmine_bonus_settings"
        ordering = ["id"]


class GoldmineBonusTransaction(models.Model):
    PENDING = 1
    AUTHORIZED = 2
    VOIDED = 3

    STATUS = [
        (1, "pending"),
        (2, "authorized"),
        (3, "voided"),
    ]

    total_invest_bonus = models.FloatField()
    level = models.IntegerField()
    bonus = models.FloatField()
    status = models.IntegerField(choices=STATUS, default=PENDING)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    user = models.ForeignKey(
        "user.User",
        on_delete=models.CASCADE,
        related_name="goldmine_bonus_transactions",
    )

    class Meta:
        db_table = "goldmine_bonus_transaction"
        ordering = ["id"]

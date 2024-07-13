from django.db import models


# Create your models here.
class Account(models.Model):
    CREDIT = 1
    SPONSOR = 2
    SHARES = 3
    TRADE = 4
    TIERING = 5

    ACCOUNT_TYPES = [
        (1, "usdt"),  # CREDIT
        (2, "sponsor"),
        (3, "shares"),
        (4, "trade"),
        (5, "tiering"),
    ]

    account_type = models.IntegerField(choices=ACCOUNT_TYPES)
    open_balance = models.FloatField(default=0)
    available_balance = models.FloatField(default=0)
    is_transferable = models.BooleanField(default=True)
    is_withdrawable = models.BooleanField(default=True)
    is_enable = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        "user.User", on_delete=models.CASCADE, related_name="accounts"
    )

    class Meta:
        db_table = "account"
        ordering = ["id"]
        unique_together = [("account_type", "user_id")]

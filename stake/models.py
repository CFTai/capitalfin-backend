from django.db import models


# Create your models here.
class Stake(models.Model):
    """
    Master Contract/Fixed Deposit
    """

    ACTIVE = 1
    EXPIRING = 2
    EXPIRED = 3
    SUSPENDED = 4
    STAKE_STATUS = [
        (1, "active"),
        (2, "expiring"),
        (3, "expired"),
        (4, "suspended"),
    ]

    amount = models.FloatField()
    shares_amount = models.FloatField(default=0)
    total_amount = models.FloatField()
    available_amount = models.FloatField(default=0)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    stake_status = models.IntegerField()
    date_created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        "user.User", on_delete=models.CASCADE, related_name="stakes"
    )
    term = models.ForeignKey(
        "term.Term", on_delete=models.CASCADE, related_name="stakes"
    )

    class Meta:
        db_table = "stake"
        ordering = ["id"]

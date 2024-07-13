from django.db import models


# Create your models here.
class Contract(models.Model):
    INACTIVE = 1
    OPEN = 2
    CLOSED = 3
    COMPLETED = 4
    SUSPENDED = 5
    CONTRACT_STATUS = [
        (1, "inactive"),
        (2, "open"),
        (3, "closed"),
        (4, "completed"),
        (5, "suspended"),
    ]

    title = models.CharField(max_length=255)
    code = models.CharField(max_length=5, null=True)
    roi_rate_from = models.FloatField(default=0)
    roi_rate_to = models.FloatField(default=0)
    share_allowance_rate = models.FloatField(default=0)
    bonus_income_cap_rate = models.FloatField(default=0)
    minimum_amount = models.FloatField(default=0)
    amount_multiple = models.FloatField(default=0)
    roi_daily_rate = models.FloatField(default=0)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    contract_status = models.IntegerField(choices=CONTRACT_STATUS, default=INACTIVE)
    term = models.ForeignKey(
        "term.Term", on_delete=models.CASCADE, related_name="contracts"
    )

    class Meta:
        db_table = "contract"
        ordering = ["id"]


class ContractRoiLog(models.Model):
    roi_rate = models.FloatField(default=0)
    date_created = models.DateTimeField(auto_now_add=True)
    contract = models.ForeignKey(
        "contract.Contract", on_delete=models.CASCADE, related_name="roi_logs"
    )

    class Meta:
        db_table = "contract_roi_log"
        ordering = ["id"]

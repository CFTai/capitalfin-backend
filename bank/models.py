from django.db import models


# Create your models here.
class Bank(models.Model):
    PENDING = 1
    AUTHORIZED = 2
    DEACTIVATED = 3
    REJECTED = 4
    BANK_STATUS = [
        (1, "pending"),
        (2, "authorized"),
        (3, "deactivated"),
        (4, "rejected"),
    ]

    account_name = models.CharField(max_length=255)
    account_number = models.CharField(max_length=255)
    bank_name = models.CharField(max_length=255)
    bank_country = models.CharField(max_length=3, help_text="Using ISO 3 country code")
    bank_region = models.CharField(max_length=255)
    bank_branch = models.CharField(max_length=255)
    bank_status = models.IntegerField(choices=BANK_STATUS, default=PENDING)
    remark = models.TextField(null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        "user.User", on_delete=models.CASCADE, related_name="banks"
    )

    class Meta:
        db_table = "bank"
        ordering = ["id"]

from django.db import models


# Create your models here.
class BlockchainWallet(models.Model):
    PENDING = 1
    AUTHORIZED = 2
    DEACTIVATED = 3
    REJECTED = 4
    WALLET_STATUS = [
        (1, "pending"),
        (2, "authorized"),
        (3, "deactivated"),
        (4, "rejected"),
    ]

    DEPOSIT = 1
    WITHDRAWAL = 2
    WALLET_TYPES = [(1, "deposit"), (2, "withdrawal")]

    wallet_address = models.CharField(max_length=255)
    wallet_type = models.IntegerField(choices=WALLET_TYPES, default=WITHDRAWAL)
    wallet_status = models.IntegerField(choices=WALLET_STATUS, default=PENDING)
    remark = models.TextField(null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        "user.User", on_delete=models.CASCADE, related_name="blockchain_wallets"
    )
    attachment = models.OneToOneField(
        "upload.Upload",
        on_delete=models.CASCADE,
        related_name="blockchain_wallet",
        unique=True,
    )

    class Meta:
        db_table = "blockchain_wallet"
        ordering = ["id"]

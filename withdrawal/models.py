from django.db import models


# Create your models here.
class WithdrawalSettings(models.Model):
    WITHDRAW_MULTIPLE = 1
    BANK_SERVICE_FEE = 2
    BANK_MINIMUM_WITHDRAW = 3
    BLOCKCHAIN_SERVICE_FEE = 4
    BLOCKCHAIN_MINIMUM_WITHDRAW = 5
    BLOCKCHAIN_GAS_FEE = 6

    SETTING_TYPES = [
        (1, "withdraw multiple"),
        (2, "bank minimum withdraw"),
        (3, "bank service fee"),
        (4, "blockchain minimum withdraw"),
        (5, "blockchain service fee"),
        (6, "blockchain gas fee"),
    ]

    settings_type = models.IntegerField(choices=SETTING_TYPES)
    description = models.CharField(max_length=255)
    rate = models.FloatField()

    class Meta:
        db_table = "withdrawal_settings"
        ordering = ["id"]


class WithdrawalBlockchain(models.Model):
    wallet_address = models.CharField(max_length=255)
    transaction_hash = models.CharField(max_length=255)
    withdrawal_date = models.DateTimeField(auto_now_add=True)
    withdrawal_transaction = models.OneToOneField(
        "transaction.Transaction",
        on_delete=models.CASCADE,
        related_name="blockchain_withdrawal",
    )
    service_fee_transaction = models.OneToOneField(
        "transaction.Transaction",
        on_delete=models.CASCADE,
        related_name="blockchain_withdrawal_service_fee",
    )
    gas_fee_transaction = models.OneToOneField(
        "transaction.Transaction",
        on_delete=models.CASCADE,
        related_name="blockchain_withdrawal_gas_fee",
    )

    class Meta:
        db_table = "withdrawal_blockchain"
        ordering = ["id"]


class WithdrawalBank(models.Model):
    account_name = models.CharField(max_length=255)
    account_number = models.CharField(max_length=255)
    bank_name = models.CharField(max_length=255)
    bank_country = models.CharField(max_length=3, help_text="Using ISO 3 country code")
    bank_region = models.CharField(max_length=255)
    bank_branch = models.CharField(max_length=255)
    withdrawal_date = models.DateTimeField(auto_now_add=True)
    withdrawal_transaction = models.OneToOneField(
        "transaction.Transaction",
        on_delete=models.CASCADE,
        related_name="bank_withdrawal",
    )
    service_fee_transaction = models.OneToOneField(
        "transaction.Transaction",
        on_delete=models.CASCADE,
        related_name="bank_withdrawal_service_fee",
    )

    class Meta:
        db_table = "withdrawal_bank"
        ordering = ["id"]

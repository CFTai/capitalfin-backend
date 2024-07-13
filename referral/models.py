from django.db import models


# Create your models here.
class Referral(models.Model):
    referrer = models.ForeignKey(
        "user.User", on_delete=models.CASCADE, related_name="downlines"
    )
    referred = models.OneToOneField(
        "user.User", on_delete=models.CASCADE, related_name="upline"
    )
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "referral"
        ordering = ["id"]
        unique_together = [("referrer_id", "referred_id")]


class ReferralNetwork(models.Model):
    DOWNLINE = 1
    UPLINE = 2

    NETWORK_TYPES = [
        (1, "downline"),
        (2, "upline"),
    ]

    user_id = models.IntegerField(primary_key=True)
    username = models.CharField(max_length=150)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    referrer_username = models.CharField(max_length=150)
    lvl = models.IntegerField()
    network = models.CharField(max_length=255)
    network_type = models.IntegerField(choices=NETWORK_TYPES)
    referrer = models.ForeignKey(
        "referral.ReferralNetwork",
        on_delete=models.CASCADE,
        null=True,
        related_name="referred_users",
    )

    class Meta:
        db_table = "referral_network"
        ordering = ["-referrer_id", "user_id"]
        managed = False
        unique_together = [("referrer_id", "user_id")]


class ReferralBonusSettings(models.Model):
    rate = models.FloatField()
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    date_updated = models.DateTimeField(auto_now=True)
    term = models.ForeignKey(
        "term.Term",
        on_delete=models.CASCADE,
        null=True,
        related_name="referral_bonus_settings",
    )

    class Meta:
        db_table = "referral_bonus_settings"
        ordering = ["id"]


class ReferralBonusTransaction(models.Model):
    PENDING = 1
    AUTHORIZED = 2
    VOIDED = 3

    STATUS = [(1, "pending"), (2, "authorized"), (3, "voided")]

    referrer = models.ForeignKey(
        "user.User",
        on_delete=models.CASCADE,
        related_name="referral_bonus_transactions",
        null=True,
    )
    term = models.ForeignKey(
        "term.Term",
        on_delete=models.CASCADE,
        related_name="referral_bonus_transactions",
        null=True,
    )
    user = models.ForeignKey(
        "user.User",
        on_delete=models.CASCADE,
        related_name="sponsor_bonus_transactions",
        null=True,
    )
    amount = models.FloatField()
    rate = models.FloatField()
    bonus = models.FloatField()
    status = models.IntegerField(choices=STATUS, default=PENDING)
    date_created = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = "referral_bonus_transaction"
        ordering = ["id"]


class ReferralRoiNetwork(models.Model):
    DOWNLINE = 1
    UPLINE = 2

    NETWORK_TYPES = [
        (1, "downline"),
        (2, "upline"),
    ]

    user_id = models.IntegerField(primary_key=True)
    referrer_username = models.CharField(max_length=150)
    lvl = models.IntegerField()
    network = models.CharField(max_length=255)
    network_type = models.IntegerField(choices=NETWORK_TYPES)
    invest_bonus = models.FloatField()
    referrer = models.ForeignKey(
        "referral.ReferralRoiNetwork",
        on_delete=models.CASCADE,
        null=True,
        related_name="referred_roi_users",
    )

    class Meta:
        db_table = "referral_roi_network"
        ordering = ["-referrer_id", "user_id"]
        managed = False

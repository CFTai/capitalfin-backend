from django.db import models


# Create your models here.
class TermSettings(models.Model):
    MINIMUM_AMOUNT = 1
    AMOUNT_MULTIPLE = 2
    EARLY_RENEWAL_DAYS = 3
    SHARES_ALLOWANCE = 4

    SETTING_TYPES = [
        (1, "minimum amount"),
        (2, "amount multiple"),
        (3, "early renewal days"),
        (4, "shares allowance rate"),
    ]

    settings_type = models.IntegerField(choices=SETTING_TYPES)
    description = models.CharField(max_length=255)
    value = models.FloatField()

    class Meta:
        db_table = "term_settings"


class Term(models.Model):
    title = models.CharField(max_length=255)
    days = models.IntegerField()
    is_enable = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "term"
        ordering = ["id"]

from django.db.models import signals, Q
from django.dispatch import receiver

from bank import models


@receiver(signals.post_save, sender=models.Bank)
def post_save(sender, instance, created, *args, **kwargs):
    try:
        if created:
            models.Bank.objects.exclude(
                Q(id=instance.id)
                | Q(bank_status__in=[models.Bank.DEACTIVATED, models.Bank.REJECTED]),
            ).filter(user_id=instance.user_id).update(
                bank_status=models.Bank.DEACTIVATED
            )
    except Exception as ex:
        pass

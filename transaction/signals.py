from django.db.models import signals
from django.dispatch import receiver

from account import tasks as account_tasks

from transaction import models


@receiver(signals.post_save, sender=models.Transaction)
def transaction_post_save(sender, instance, created, *args, **kwargs):
    account_tasks.account_update_available_balance(instance.account.id)

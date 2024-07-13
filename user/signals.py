from django.db.models import signals
from django.dispatch import receiver

from account import tasks as account_tasks

from user import models


@receiver(signals.post_save, sender=models.User)
def post_save(sender, instance, created, *args, **kwargs):
    try:
        if created and instance.is_staff is False:
            account_tasks.account_create_new_user.delay(instance.id)
    except Exception as ex:
        pass

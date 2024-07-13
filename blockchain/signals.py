from django.db.models import signals, Q
from django.dispatch import receiver

from blockchain import models


@receiver(signals.post_save, sender=models.BlockchainWallet)
def post_save(sender, instance, created, *args, **kwargs):
    try:
        if created:
            models.BlockchainWallet.objects.exclude(
                Q(id=instance.id)
                | Q(
                    wallet_status__in=[
                        models.BlockchainWallet.DEACTIVATED,
                        models.BlockchainWallet.REJECTED,
                    ]
                ),
            ).filter(user_id=instance.user_id, wallet_type=instance.wallet_type).update(
                wallet_status=models.BlockchainWallet.DEACTIVATED
            )
    except Exception as ex:
        pass

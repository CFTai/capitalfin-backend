from django.utils import timezone

from celery import shared_task

from stake.models import Stake


@shared_task(name="stake_status_update")
def stake_status_update():
    # Todo return to credit account (USDT) from total amount
    today = timezone.datetime.combine(
        timezone.now().date(), timezone.datetime.max.time()
    )

    # All Stake that ACTIVE or EXPIRING to EXPIRED
    Stake.objects.filter(
        end_date__lte=today, stake_status__in=[Stake.ACTIVE, Stake.EXPIRING]
    ).update(stake_status=Stake.EXPIRED)

    expiring_date = today + timezone.timedelta(days=30)
    # All Stake that ACTIVE is expiring in 30 days
    Stake.objects.filter(end_date__lte=expiring_date, stake_status=Stake.ACTIVE).update(
        stake_status=Stake.EXPIRING
    )

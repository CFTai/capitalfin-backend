from celery import shared_task, chain

from stake.tasks import stake_status_update

from contract.tasks import contract_roi_generator

from invest.tasks import invest_bonus_process, invest_bonus_release

from goldmine.tasks import goldmine_bonus_process, goldmine_bonus_release

from referral.tasks import referral_bonus_release


@shared_task(name="daily_process")
def daily_process():
    chain(
        stake_status_update.si(),
        # contract_roi_generator.si(),
        invest_bonus_process.si(),
        # goldmine_bonus_process.si(),
        invest_bonus_release.si(),
        referral_bonus_release.si(),
    )()


@shared_task(name="monthly_process")
def monthly_process():
    pass
    # goldmine_bonus_release.delay()

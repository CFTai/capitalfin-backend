from django.utils import timezone
from django.db import models as django_models
from celery import shared_task

from account import models as account_models
from transaction import models as transaction_models
from contract import models as contract_models
from invest import models


@shared_task(name="invest_status_update")
def invest_status_update():
    # Todo return to credit account (USDT) from total amount
    today = timezone.datetime.combine(
        timezone.now().date(), timezone.datetime.max.time()
    )

    models.Invest.objects.filter(
        end_date__lte=today, status__in=[models.Invest.ACTIVE]
    ).update(status=models.Invest.COMPLETED)


@shared_task(name="invest_bonus_process")
def invest_bonus_process():
    for invest in models.Invest.objects.filter(status=models.Invest.ACTIVE):
        invest_bonus_calculator.delay(invest.id, invest.contract.roi_daily_rate)


@shared_task(name="invest_bonus_calculator")
def invest_bonus_calculator(invest_id, roi_daily_rate):
    invest = models.Invest.objects.get(id=invest_id)
    bonus = invest.total_amount * roi_daily_rate
    estimate_total_payout = bonus + invest.bonus_total_payout
    payout_bonus = 0

    if estimate_total_payout <= invest.bonus_income_cap:
        payout_bonus = bonus
    elif estimate_total_payout > invest.bonus_income_cap:
        payout_bonus = estimate_total_payout - invest.bonus_income_cap
        payout_bonus = bonus - payout_bonus

    models.InvestBonusTransaction.objects.create(
        amount=invest.total_amount,
        rate=roi_daily_rate,
        bonus=payout_bonus,
        invest=invest,
    )


@shared_task(name="invest_bonus_release")
def invest_bonus_release():
    bonus_transactions = (
        models.InvestBonusTransaction.objects.filter(
            status=models.InvestBonusTransaction.PROCESSING,
        )
        .values("invest_id")
        .annotate(bonus_sum=django_models.Sum("bonus"))
    )
    for bonus_transaction in bonus_transactions:
        invest_bonus_payout.delay(
            bonus_transaction.get("invest_id"),
            bonus_transaction.get("bonus_sum"),
        )


@shared_task(name="invest_bonus_payout")
def invest_bonus_payout(invest_id, bonus_sum):
    invest = models.Invest.objects.get(id=invest_id)
    user = invest.stake.user
    trade_account = user.accounts.get(account_type=account_models.Account.TRADE)
    transaction_models.Transaction.objects.create(
        amount=bonus_sum,
        remark=f"REF: sub-contract #{invest.id}",
        transaction_type=transaction_models.Transaction.TRADING_BONUS,
        account=trade_account,
    )
    models.InvestBonusTransaction.objects.filter(
        status=models.InvestBonusTransaction.PROCESSING, invest_id=invest_id
    ).update(status=models.InvestBonusTransaction.AUTHORIZED)

    invest.bonus_total_payout += bonus_sum
    invest.status = (
        models.Invest.PAID
        if invest.bonus_total_payout >= invest.bonus_income_cap
        else invest.status
    )
    invest.save()

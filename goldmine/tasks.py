from celery import shared_task

from django.db.models import Sum

from user.models import User

from account.models import Account

from transaction.models import Transaction

from referral.models import ReferralRoiNetwork
from referral.operations import ReferralOperations

from stake.models import Stake

from invest.models import Invest

from goldmine.models import GoldmineBonusSettings, GoldmineBonusTransaction


@shared_task(name="goldmine_bonus_process")
def goldmine_bonus_process():
    # Get the minimum term in goldmine settings
    list_term_id = GoldmineBonusSettings.objects.values_list("term_id")
    # Invest status must be active filter by stake's term that higher than term_id 1, then group by stake
    eligible_users = Invest.objects.filter(
        invest_status=Invest.ACTIVE,
        stake__stake_status=Stake.ACTIVE,
        stake__term_id__in=list_term_id,
    ).values("stake__user_id", "stake__term_id")
    for user in eligible_users:
        goldmine_bonus_calculator.delay(user["stake__user_id"], user["stake__term_id"])


@shared_task(name="goldmine_bonus_calculator")
def goldmine_bonus_calculator(user_id, term_id):
    bonus_settings = GoldmineBonusSettings.objects.get(term_id=term_id)
    ReferralOperations().sp_referral_roi_network(user_id)
    for i in range(bonus_settings.max_level):
        total_invest_bonus = (
            ReferralRoiNetwork.objects.filter(lvl=i + 1)
            .aggregate(Sum("invest_bonus"))
            .get("invest_bonus__sum", 0)
        )
        if total_invest_bonus is not None and total_invest_bonus > 0:
            bonus = bonus_settings.rate * total_invest_bonus
            GoldmineBonusTransaction.objects.create(
                total_invest_bonus=total_invest_bonus,
                level=i + 1,
                bonus=bonus,
                user_id=user_id,
            )


@shared_task(name="goldmine_bonus_release")
def goldmine_bonus_release():
    transactions = (
        GoldmineBonusTransaction.objects.filter(status=GoldmineBonusTransaction.PENDING)
        .values("user_id")
        .annotate(bonus_sum=Sum("bonus"))
    )
    for transaction in transactions:
        goldmine_bonus_payout.delay(
            transaction.get("user_id"),
            transaction.get("bonus_sum"),
        )


@shared_task(name="goldmine_bonus_payout")
def goldmine_bonus_payout(user_id, bonus_sum):
    user = User.objects.get(id=user_id)
    # Goldmine account
    tiering_account = user.accounts.get(account_type=Account.TIERING)
    Transaction.objects.create(
        amount=bonus_sum,
        transaction_type=Transaction.TIERING_BONUS,
        account=tiering_account,
    )
    GoldmineBonusTransaction.objects.filter(
        user_id=user_id, status=GoldmineBonusTransaction.PENDING
    ).update(status=GoldmineBonusTransaction.AUTHORIZED)

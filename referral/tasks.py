from django.db import models as django_models

from celery import shared_task

from user import models as user_models

from account import models as account_models

from transaction import models as transaction_models

from referral import models


@shared_task(name="referral_registered")
def referral_registered(referrer_id, user_id):
    models.Referral.objects.create(
        referrer_id=referrer_id,
        referred_id=user_id,
    )


@shared_task(name="referral_bonus_calculator")
def referral_bonus_calculator(user_id, term_id, amount):
    # Find referrer and bonus rate
    referral = models.Referral.objects.filter(referred_id=user_id).first()
    if referral is not None:
        bonus_settings = models.ReferralBonusSettings.objects.filter(
            term_id=term_id
        ).first()
        if bonus_settings is not None:
            bonus = amount * bonus_settings.rate
            models.ReferralBonusTransaction.objects.create(
                referrer_id=referral.referrer.id,
                user_id=user_id,
                term_id=term_id,
                amount=amount,
                rate=bonus_settings.rate,
                bonus=bonus,
            )


@shared_task(name="referral_bonus_release")
def referral_bonus_release():
    bonus_transactions = (
        models.ReferralBonusTransaction.objects.filter(
            status=models.ReferralBonusTransaction.PENDING
        )
        .values("referrer_id", "user_id")
        .annotate(bonus_sum=django_models.Sum("bonus"))
    )
    for bonus_transaction in bonus_transactions:
        referral_bonus_payout.delay(
            bonus_transaction.get("referrer_id"),
            bonus_transaction.get("user_id"),
            bonus_transaction.get("bonus_sum"),
        )


@shared_task(name="referral_bonus_payout")
def referral_bonus_payout(referrer_id, user_id, bonus_sum):
    sponsor_bonus_account = account_models.Account.objects.get(
        account_type=account_models.Account.SPONSOR, user_id=referrer_id
    )
    user = user_models.User.objects.get(id=user_id)
    transaction_models.Transaction.objects.create(
        amount=bonus_sum,
        remark=f"REF: Referral bonus {user.username}",
        transaction_type=transaction_models.Transaction.SPONSOR_BONUS,
        account=sponsor_bonus_account,
    )
    models.ReferralBonusTransaction.objects.filter(
        status=models.ReferralBonusTransaction.PENDING,
        referrer_id=referrer_id,
        user_id=user_id,
    ).update(status=models.ReferralBonusTransaction.AUTHORIZED)

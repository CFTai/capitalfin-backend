from django.db import models as m

from celery import shared_task

from transaction import models as transaction_models

from account import models


@shared_task(name="account_create_new_user")
def account_create_new_user(user_id):
    for i in models.Account.ACCOUNT_TYPES:
        disabled = [models.Account.SHARES]
        is_enable = False if i[0] in disabled else True
        models.Account.objects.create(
            account_type=i[0], user_id=user_id, is_enable=is_enable
        )


@shared_task(name="account_update_available_balance")
def account_update_available_balance(account_id):
    account = models.Account.objects.get(id=account_id)
    sum = account.transactions.exclude(
        transaction_status=transaction_models.Transaction.VOIDED
    ).aggregate(balance=m.Sum("amount"))

    account.available_balance = 0 if sum["balance"] is None else sum["balance"]
    account.save()

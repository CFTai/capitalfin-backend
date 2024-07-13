from unittest.mock import patch, Mock

from django.utils import timezone
from django.test import TestCase

from user.models import User

from account.models import Account
from account.tests import patch_task_account_create_new_user

from referral.models import Referral

from stake.models import Stake

from contract.models import Contract

from invest import tasks as invest_tasks
from invest.models import Invest

from goldmine import tasks


# Create your tests here.
class GoldmineTestCase(TestCase):
    @patch_task_account_create_new_user
    def setUp(self) -> None:
        for i in range(15):
            User.objects.create(username=f"user_{i}")

        referral_list = []
        for i in range(1, 15, 2):
            referral_list.append(Referral(referrer_id=i, referred_id=i + 1))
        for i in range(2, 15, 2):
            referral_list.append(Referral(referrer_id=i, referred_id=i + 1))
        Referral.objects.bulk_create(referral_list)

        stake_list = []
        for i in range(1, 16):
            stake_list.append(
                Stake(
                    amount=1000,
                    total_amount=1000,
                    start_date=timezone.now(),
                    end_date=timezone.now(),
                    stake_status=Stake.ACTIVE,
                    user_id=i,
                    term_id=2,
                )
            )
        Stake.objects.bulk_create(stake_list)

        Contract.objects.create(
            title="Contract 1",
            roi_rate=0.1,
            contract_status=Contract.CLOSED,
            term_id=2,
        )

        invest_list = []
        for i in range(1, 16):
            invest_list.append(Invest(amount=1000, contract_id=1, stake_id=i))
        Invest.objects.bulk_create(invest_list)

    @patch(
        "goldmine.tasks.goldmine_bonus_calculator.delay",
        Mock(wraps=tasks.goldmine_bonus_calculator),
    )
    @patch(
        "goldmine.tasks.goldmine_bonus_payout.delay",
        Mock(wraps=tasks.goldmine_bonus_payout),
    )
    @patch(
        "invest.tasks.invest_bonus_calculator.delay",
        Mock(wraps=invest_tasks.invest_bonus_calculator),
    )
    def test_goldmine_process(self):
        invest_tasks.invest_bonus_process()
        tasks.goldmine_bonus_process()
        tasks.goldmine_bonus_release()

        tiering_account = Account.objects.get(
            user=User.objects.get(username="user_1"), account_type=Account.TIERING
        )
        self.assertEqual(5, tiering_account.available_balance)

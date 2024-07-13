from unittest.mock import patch, Mock

from django.contrib import auth
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate

from user import models as user_models

from account import models as account_models, tests as account_tests

from stake import views as stake_views, models as stake_models

from referral import models, tasks

patch_task_referral_registered = patch(
    "referral.tasks.referral_registered.delay", Mock(wraps=tasks.referral_registered)
)

patch_task_referral_bonus_calculator = patch(
    "referral.tasks.referral_bonus_calculator.delay",
    Mock(wraps=tasks.referral_bonus_calculator),
)


# Create your tests here.
class ReferralBonusTransactionTestCase(APITestCase):
    @account_tests.patch_task_account_create_new_user
    def setUp(self) -> None:
        self.factory = APIRequestFactory()
        self.auth_user = user_models.User.objects.create(
            username="user",
            status=user_models.User.VERIFIED,
            transaction_password=auth.hashers.make_password("P@ssw0rd"),
        )
        self.referrer = user_models.User.objects.create(
            username="referrer",
            status=user_models.User.VERIFIED,
            transaction_password=auth.hashers.make_password("P@ssw0rd"),
        )
        models.Referral.objects.create(referrer=self.referrer, referred=self.auth_user)

    @patch_task_referral_bonus_calculator
    def test_post_referral_bonus_purchase(self):
        term_id = 1
        amount = 1000

        account_models.Account.objects.filter(
            account_type=account_models.Account.CREDIT, user=self.auth_user
        ).update(available_balance=amount)

        data = {"amount": amount, "term": term_id, "transaction_password": "P@ssw0rd"}
        request = self.factory.post("/stakes/quote/", data)
        force_authenticate(request, self.auth_user)
        response = stake_views.StakeAPIView.as_view()(request)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        record = stake_models.Stake.objects.get(
            user=self.auth_user, stake_status=stake_models.Stake.ACTIVE
        )
        self.assertIsInstance(record, stake_models.Stake)

        bonus_transaction = models.ReferralBonusTransaction.objects.get(
            referrer_id=self.referrer.id, user_id=self.auth_user.id
        )
        self.assertIsInstance(bonus_transaction, models.ReferralBonusTransaction)
        self.assertEqual(
            bonus_transaction.status, models.ReferralBonusTransaction.PENDING
        )
        bonus_settings = models.ReferralBonusSettings.objects.get(term_id=term_id)
        self.assertEqual(bonus_settings.rate * amount, bonus_transaction.bonus)

    @patch_task_referral_bonus_calculator
    def test_post_referral_bonus_upgrade(self):
        term_id = 2
        amount = 2000
        end_date = timezone.now()

        stake = stake_models.Stake.objects.create(
            amount=1000,
            total_amount=1000,
            start_date=end_date,
            end_date=end_date,
            user=self.auth_user,
            term_id=1,
            stake_status=stake_models.Stake.ACTIVE,
        )
        account_models.Account.objects.filter(
            account_type=account_models.Account.CREDIT, user=self.auth_user
        ).update(available_balance=amount)

        data = {"amount": amount, "term": term_id, "transaction_password": "P@ssw0rd"}
        request = self.factory.post("/stakes/quote/topup/", data)
        force_authenticate(request, self.auth_user)
        response = stake_views.StakeTopupAPIView.as_view()(request)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        stake.refresh_from_db()
        self.assertEqual(2, stake.term.id)
        self.assertGreater(stake.end_date, end_date)

        bonus_transaction = models.ReferralBonusTransaction.objects.get(
            referrer_id=self.referrer.id, user_id=self.auth_user.id
        )
        self.assertIsInstance(bonus_transaction, models.ReferralBonusTransaction)
        self.assertEqual(
            bonus_transaction.status, models.ReferralBonusTransaction.PENDING
        )
        bonus_settings = models.ReferralBonusSettings.objects.get(term_id=term_id)
        self.assertEqual(bonus_settings.rate * amount, bonus_transaction.bonus)

    def test_post_referral_bonus_upgrade_without_amount(self):
        term_id = 2
        amount = 0
        end_date = timezone.now()

        stake = stake_models.Stake.objects.create(
            amount=1000,
            total_amount=1000,
            start_date=end_date,
            end_date=end_date,
            user=self.auth_user,
            term_id=1,
            stake_status=stake_models.Stake.ACTIVE,
        )

        data = {"amount": amount, "term": term_id, "transaction_password": "P@ssw0rd"}
        request = self.factory.post("/stakes/quote/topup/", data)
        force_authenticate(request, self.auth_user)
        response = stake_views.StakeTopupAPIView.as_view()(request)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        stake.refresh_from_db()
        self.assertEqual(2, stake.term.id)
        self.assertGreater(stake.end_date, end_date)

        bonus_transaction = models.ReferralBonusTransaction.objects.filter(
            referrer_id=self.referrer.id, user_id=self.auth_user.id
        ).first()
        self.assertIsNone(bonus_transaction)

    @patch(
        "referral.tasks.referral_bonus_payout.delay",
        Mock(wraps=tasks.referral_bonus_payout),
    )
    def test_task_referral_bonus_release(self):
        transactions = [
            models.ReferralBonusTransaction(
                referrer_id=self.referrer.id,
                term_id=1,
                user_id=self.auth_user.id,
                amount=1000,
                rate=0.1,
                bonus=100,
            ),
            models.ReferralBonusTransaction(
                referrer_id=self.referrer.id,
                term_id=1,
                user_id=self.auth_user.id,
                amount=1000,
                rate=0.1,
                bonus=100,
            ),
            models.ReferralBonusTransaction(
                referrer_id=self.referrer.id,
                term_id=1,
                user_id=self.auth_user.id,
                amount=3000,
                rate=0.1,
                bonus=300,
            ),
        ]
        models.ReferralBonusTransaction.objects.bulk_create(transactions)
        tasks.referral_bonus_release()

        sponsor_bonus_account = self.referrer.accounts.get(
            account_type=account_models.Account.SPONSOR
        )
        self.assertEqual(500, sponsor_bonus_account.available_balance)

from unittest.mock import patch, Mock
from django.contrib import auth
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate

from user import models as user_models
from account import tests as account_tests, models as account_models
from referral import tests as referral_tests
from stake import models as stake_models
from contract import models as contract_models
from invest import views, models, tasks


# Create your tests here.
class InvestAPITestCase(APITestCase):
    @account_tests.patch_task_account_create_new_user
    def setUp(self) -> None:
        self.factory = APIRequestFactory()

        # Mock user
        self.auth_user = user_models.User.objects.create(
            username="user_1",
            transaction_password=auth.hashers.make_password("password"),
        )

        # Mock account balance
        account_models.Account.objects.filter(
            account_type=account_models.Account.CREDIT, user=self.auth_user
        ).update(available_balance=1000)
        account_models.Account.objects.filter(
            account_type=account_models.Account.SHARES, user=self.auth_user
        ).update(available_balance=1000)

        # Mock stake/master contract
        end_date = timezone.now()
        self.stake = stake_models.Stake.objects.create(
            amount=1000,
            total_amount=0,
            start_date=timezone.now(),
            end_date=end_date,
            user=self.auth_user,
            term_id=1,
            stake_status=stake_models.Stake.ACTIVE,
        )

        # Mock contract
        self.contract_1 = contract_models.Contract.objects.create(
            title="Contract 1",
            share_allowance_rate=0.5,
            bonus_income_cap_rate=3,
            minimum_amount=1000.0,
            amount_multiple=10.0,
            term_id=1,
            roi_daily_rate=0.0025,
            contract_status=contract_models.Contract.OPEN,
        )

    def test_post_invest_quote(self):
        data = {"amount": 1000, "contract": self.contract_1.id}
        request = self.factory.post("/invests/quote/", data)
        force_authenticate(request, self.auth_user)
        response = views.InvestQuoteAPIView.as_view()(request)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(1000, response.data["amount"])

    def test_post_invest_insufficient_balance(self):
        data = {"amount": 2000, "contract": self.contract_1.id}
        request = self.factory.post("/invests/quote/", data)
        force_authenticate(request, self.auth_user)
        response = views.InvestQuoteAPIView.as_view()(request)

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        error = response.data["amount"]
        self.assertEqual("Insufficient account balance.", error[0])

    def test_post_invest_shares_quote(self):
        data = {"amount": 1000, "contract": self.contract_1.id, "share_percentage": 50}
        request = self.factory.post("/invests/quote/", data)
        force_authenticate(request, self.auth_user)
        response = views.InvestQuoteAPIView.as_view()(request)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(1000, response.data["amount"])

    def test_post_invest_insufficient_shares_quote(self):
        data = {"amount": 3000, "contract": self.contract_1.id, "share_percentage": 50}
        request = self.factory.post("/invests/quote/", data)
        force_authenticate(request, self.auth_user)
        response = views.InvestQuoteAPIView.as_view()(request)

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

        error = response.data["share_percentage"]
        self.assertEqual("Insufficient account balance.", error[0])

    def test_post_invest_validate_minimum_amount_quote(self):
        data = {"amount": 500, "contract": self.contract_1.id, "share_percentage": 60}
        request = self.factory.post("/invests/quote/", data)
        force_authenticate(request, self.auth_user)

        response = views.InvestQuoteAPIView.as_view()(request)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        error = response.data["amount"]
        self.assertEqual(
            f"Amount must greater then contract minimum amount {self.contract_1.minimum_amount}.",
            error[0],
        )

    def test_post_invest_validate_amount_multiple_quote(self):
        data = {"amount": 1001, "contract": self.contract_1.id, "share_percentage": 60}
        request = self.factory.post("/invests/quote/", data)
        force_authenticate(request, self.auth_user)

        response = views.InvestQuoteAPIView.as_view()(request)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        error = response.data["amount"]
        self.assertEqual(
            f"Amount must multiple by {self.contract_1.amount_multiple}", error[0]
        )

    def test_post_invest_validate_shares_limit_quote(self):
        data = {"amount": 1000, "contract": self.contract_1.id, "share_percentage": 60}
        request = self.factory.post("/invests/quote/", data)
        force_authenticate(request, self.auth_user)

        response = views.InvestQuoteAPIView.as_view()(request)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        error = response.data["share_percentage"]
        self.assertEqual("Percentage exceed systems limit.", error[0])

    def test_post_invest_validate_stack_status_quote(self):
        self.stake.stake_status = stake_models.Stake.EXPIRED
        self.stake.save()

        data = {"amount": 1000, "contract": self.contract_1.id, "share_percentage": 60}
        request = self.factory.post("/invests/quote/", data)
        force_authenticate(request, self.auth_user)

        response = views.InvestQuoteAPIView.as_view()(request)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        error = response.data["contract"]
        self.assertEqual("Ineligible to invest.", error[0])

    @referral_tests.patch_task_referral_bonus_calculator
    def test_post_invest_purchase(self):
        data = {
            "amount": 1000,
            "contract": self.contract_1.id,
            "transaction_password": "password",
        }
        request = self.factory.post("/invests/", data)
        force_authenticate(request, self.auth_user)
        response = views.InvestAPIView.as_view()(request)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        record = models.Invest.objects.get(stake__user=self.auth_user)
        self.assertIsInstance(record, models.Invest)
        self.assertEqual(record.amount, 1000)
        self.assertEqual(record.total_amount, 1000)
        self.assertEqual(
            record.bonus_income_cap, 1000 * self.contract_1.bonus_income_cap_rate
        )

    @referral_tests.patch_task_referral_bonus_calculator
    def test_post_invest_shares_purchase(self):
        data = {
            "amount": 1000,
            "contract": self.contract_1.id,
            "share_percentage": 50,
            "transaction_password": "password",
        }
        request = self.factory.post("/invests/", data)
        force_authenticate(request, self.auth_user)
        response = views.InvestAPIView.as_view()(request)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        record = models.Invest.objects.get(stake__user=self.auth_user)
        self.assertIsInstance(record, models.Invest)
        self.assertEqual(record.shares_amount, 500)
        self.assertEqual(record.total_amount, 1000)

    def test_task_invest_status_update(self):
        invest_1 = models.Invest.objects.create(
            amount=1000,
            start_date=timezone.now(),
            end_date=timezone.now(),
            contract=self.contract_1,
            stake=self.stake,
        )
        tasks.invest_status_update()

        self.assertEqual(invest_1.status, models.Invest.ACTIVE)
        invest_1.refresh_from_db()
        self.assertEqual(invest_1.status, models.Invest.COMPLETED)

    @account_tests.patch_task_account_update_available_balance
    @patch(
        "invest.tasks.invest_bonus_calculator.delay",
        Mock(wraps=tasks.invest_bonus_calculator),
    )
    @patch(
        "invest.tasks.invest_bonus_payout.delay",
        Mock(wraps=tasks.invest_bonus_payout),
    )
    def test_task_invest_bonus_process(self):
        # test basic calculation
        invest_1 = models.Invest.objects.create(
            amount=1000,
            total_amount=1000,
            bonus_income_cap=3000,
            start_date=timezone.now(),
            end_date=timezone.now(),
            contract=self.contract_1,
            stake=self.stake,
        )
        # test remaining payout
        invest_2 = models.Invest.objects.create(
            amount=2000,
            total_amount=1000,
            bonus_income_cap=5,
            bonus_total_payout=3.5,
            start_date=timezone.now(),
            end_date=timezone.now(),
            contract=self.contract_1,
            stake=self.stake,
        )
        tasks.invest_bonus_process()

        bonus_transaction = models.InvestBonusTransaction.objects.get(invest=invest_1)
        self.assertEqual(bonus_transaction.bonus, 2.5)

        bonus_transaction = models.InvestBonusTransaction.objects.get(invest=invest_2)
        bonus_transaction.status
        self.assertEqual(bonus_transaction.bonus, 1.5)

        tasks.invest_bonus_release()

        trade_account = self.auth_user.accounts.get(
            account_type=account_models.Account.TRADE
        )
        self.assertEqual(trade_account.available_balance, 1.5 + 2.5)
        bonus_transaction.refresh_from_db()
        self.assertEqual(
            bonus_transaction.status, models.InvestBonusTransaction.AUTHORIZED
        )

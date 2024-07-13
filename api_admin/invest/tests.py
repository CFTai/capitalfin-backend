from django.utils import timezone

from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate

from user import models as user_models

from stake import models as stake_models

from contract import models as contract_models

from invest import models

from api_admin.invest import views


class AdminInvestAPITestCase(APITestCase):
    def setUp(self) -> None:
        self.factory = APIRequestFactory()
        self.auth_user = user_models.User.objects.create(
            username="admin", is_staff=True
        )
        self.user = user_models.User.objects.create(username="user_1")

        # Mock stake/master contract
        end_date = timezone.now()
        stake = stake_models.Stake.objects.create(
            amount=1000,
            total_amount=0,
            start_date=timezone.now(),
            end_date=end_date,
            user=self.user,
            term_id=1,
            stake_status=stake_models.Stake.ACTIVE,
        )

        # Mock contract
        contract = contract_models.Contract.objects.create(
            title="Contract 1",
            share_allowance_rate=0.5,
            bonus_income_cap_rate=3,
            minimum_amount=1000.0,
            amount_multiple=10.0,
            term_id=1,
            roi_daily_rate=0.0025,
            contract_status=contract_models.Contract.OPEN,
        )

        # Mock invest
        self.invest = models.Invest.objects.create(
            amount=1000, contract=contract, stake=stake
        )

    def test_get_admin_invests(self):
        request = self.factory.get("/admin/invests/")
        force_authenticate(request, self.auth_user)
        response = views.AdminInvestAPIView.as_view()(request)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertIn("results", response.data)
        result = response.data["results"][0]
        self.assertEqual(self.invest.id, result["id"])

    def test_get_admin_search_invests(self):
        params = {"search": "user_1"}
        request = self.factory.get("/admin/invests/", params)
        force_authenticate(request, self.auth_user)
        response = views.AdminInvestAPIView.as_view()(request)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertIn("results", response.data)
        result = response.data["results"][0]
        self.assertEqual(self.invest.id, result["id"])

    def test_get_admin_invest_details(self):
        request = self.factory.get("/admin/invests/")
        force_authenticate(request, self.auth_user)
        response = views.AdminInvestDetailsAPIView.as_view()(request, pk=self.invest.id)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(self.invest.id, response.data["id"])

    def test_patch_admin_invest_details(self):
        data = {"status": models.Invest.SUSPENDED}
        request = self.factory.patch("/admin/invests/", data)
        force_authenticate(request, self.auth_user)
        response = views.AdminInvestDetailsAPIView.as_view()(request, pk=self.invest.id)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.invest.refresh_from_db()
        self.assertEqual(self.invest.id, response.data["id"])
        self.assertEqual(self.invest.status, models.Invest.SUSPENDED)


class AdminInvestBonusTransactionAPITestCast(APITestCase):
    def setUp(self) -> None:
        self.factory = APIRequestFactory()
        self.auth_user = user_models.User.objects.create(
            username="admin", is_staff=True
        )
        user_1 = user_models.User.objects.create(username="user_1")
        user_2 = user_models.User.objects.create(username="user_2")

        contract_1 = contract_models.Contract.objects.create(
            title="contract_1", term_id=1
        )
        contract_2 = contract_models.Contract.objects.create(
            title="contract_2", term_id=1
        )

        stake_1 = stake_models.Stake.objects.create(
            amount=1000,
            total_amount=1000,
            start_date=timezone.now(),
            end_date=timezone.now(),
            stake_status=stake_models.Stake.ACTIVE,
            user=user_1,
            term_id=1,
        )

        stake_2 = stake_models.Stake.objects.create(
            amount=1000,
            total_amount=1000,
            start_date=timezone.now(),
            end_date=timezone.now(),
            stake_status=stake_models.Stake.ACTIVE,
            user=user_2,
            term_id=1,
        )

        invests = [
            models.Invest(amount=1000, contract=contract_1, stake=stake_1),
            models.Invest(amount=1000, contract=contract_2, stake=stake_1),
            models.Invest(amount=1000, contract=contract_1, stake=stake_2),
        ]
        models.Invest.objects.bulk_create(invests)

        bonus_transactions = [
            models.InvestBonusTransaction(
                amount=1000, rate=0.1, bonus=100, invest_id=1
            ),
            models.InvestBonusTransaction(
                amount=1000, rate=0.1, bonus=100, invest_id=2
            ),
            models.InvestBonusTransaction(
                amount=1000, rate=0.1, bonus=100, invest_id=3
            ),
        ]
        models.InvestBonusTransaction.objects.bulk_create(bonus_transactions)

    def test_get_admin_invest_bonus_transactions(self):
        request = self.factory.get("/admin/invests/bonus/")
        force_authenticate(request, self.auth_user)
        response = views.AdminInvestBonusTransactionAPIView.as_view()(request)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertIn("results", response.data)

    def test_get_admin_search_invest_bonus_transactions(self):
        transactions = models.InvestBonusTransaction.objects.filter(
            invest__stake__user__username="user_1"
        )
        params = {"search": "user_1"}
        request = self.factory.get("/admin/invests/bonus/", params)
        force_authenticate(request, self.auth_user)
        response = views.AdminInvestBonusTransactionAPIView.as_view()(request)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertIn("results", response.data)
        results = response.data["results"]
        self.assertEqual(transactions.count(), len(results))
        self.assertEqual(
            transactions[0].invest.stake.user.username,
            results[0]["invest_stake_user_username"],
        )

    def test_get_admin_invest_bonus_transaction_details(self):
        transaction = models.InvestBonusTransaction.objects.all().first()
        request = self.factory.get("/admin/invests/bonus/")
        force_authenticate(request, self.auth_user)
        response = views.AdminInvestBonusTransactionDetailsAPIView.as_view()(
            request, pk=transaction.id
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(transaction.id, response.data["id"])

    def test_patch_admin_invest_bonus_transaction_details(self):
        transaction = models.InvestBonusTransaction.objects.all().first()
        data = {"status": 3}
        request = self.factory.patch("/admin/invests/bonus/", data)
        force_authenticate(request, self.auth_user)
        response = views.AdminInvestBonusTransactionDetailsAPIView.as_view()(
            request, pk=transaction.id
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        transaction.refresh_from_db()
        self.assertEqual(transaction.id, response.data["id"])
        self.assertEqual(transaction.status, response.data["status"])

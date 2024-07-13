from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate

from user import models as user_models

from account import models as account_models, tests as account_tests

from transaction import models, views


# Create your tests here.
class TransactionAPITestCase(APITestCase):
    @account_tests.patch_task_account_create_new_user
    def setUp(self) -> None:
        self.auth_user = user_models.User.objects.create(
            username="testuser",
            email="test@unittest.com",
        )
        self.transaction = models.Transaction.objects.create(
            amount=100,
            transaction_type=models.Transaction.ADMIN_TRANSACTION,
            account=self.auth_user.accounts.get(
                account_type=account_models.Account.CREDIT
            ),
        )
        models.Transaction.objects.create(
            amount=200,
            transaction_type=models.Transaction.DEPOSIT_TRANSACTION,
            account=self.auth_user.accounts.get(
                account_type=account_models.Account.CREDIT
            ),
        )
        self.withdrawal = models.Transaction.objects.create(
            amount=-300,
            transaction_type=models.Transaction.WITHDRAWAL_TRANSACTION,
            account=self.auth_user.accounts.get(
                account_type=account_models.Account.CREDIT
            ),
        )
        models.Transaction.objects.create(
            amount=100,
            transaction_type=models.Transaction.TIERING_BONUS,
            account=self.auth_user.accounts.get(
                account_type=account_models.Account.CREDIT
            ),
        )
        self.factory = APIRequestFactory()

    def test_get_transactions(self):
        view = views.TransactionAPIView.as_view()
        request = self.factory.get("/transactions/")
        force_authenticate(request, self.auth_user)
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)

        first_result = response.data["results"][0]
        self.assertEqual(100, first_result["amount"])
        self.assertEqual("admin_transaction", first_result["transaction_type_display"])

    def test_get_transactions_filter(self):
        models.Transaction.objects.create(
            amount=100,
            transaction_type=models.Transaction.TRADING_BONUS,
            account=self.auth_user.accounts.get(
                account_type=account_models.Account.TRADE
            ),
        )
        params = {"account_type": account_models.Account.TRADE}
        view = views.TransactionAPIView.as_view()
        request = self.factory.get("/transactions/", params)
        force_authenticate(request, self.auth_user)
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        first_result = response.data["results"][0]
        self.assertEqual("trade", first_result["account_type_display"])

    def test_get_transactions_ordering(self):
        params = {"ordering": "-id"}
        view = views.TransactionAPIView.as_view()
        request = self.factory.get("/transactions/", params)
        force_authenticate(request, self.auth_user)
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)

        last_transaction = (
            models.Transaction.objects.filter(
                account=self.auth_user.accounts.get(
                    account_type=account_models.Account.CREDIT
                )
            )
            .order_by("-id")
            .first()
        )
        first_result = response.data["results"][0]
        self.assertEqual(last_transaction.id, first_result["id"])

    def test_get_transaction_details(self):
        view = views.TransactionDetailsAPIView.as_view()
        request = self.factory.get("/transactions")
        force_authenticate(request, self.auth_user)
        response = view(request, pk=self.transaction.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.transaction.id, response.data["id"])

    def test_patch_transaction_details(self):
        data = {"transaction_status": models.Transaction.VOIDED}
        view = views.TransactionDetailsAPIView.as_view()
        request = self.factory.patch("/transactions", data)
        force_authenticate(request, self.auth_user)
        response = view(request, pk=self.withdrawal.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(models.Transaction.VOIDED, response.data["transaction_status"])

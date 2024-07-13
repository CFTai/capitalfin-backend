from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate

from user import models as user_models

from account import models as account_models, tests as account_tests

from transaction import models

from api_admin.transaction import views


class AdminTransactionAPITestCase(APITestCase):
    @account_tests.patch_task_account_create_new_user
    def setUp(self) -> None:
        self.factory = APIRequestFactory()

        self.auth_user = user_models.User.objects.create(
            username="admin", is_staff=True
        )

        self.user_1 = user_models.User.objects.create(username="user_1")
        models.Transaction.objects.create(
            amount=100,
            transaction_type=models.Transaction.ADMIN_TRANSACTION,
            account=self.user_1.accounts.get(
                account_type=account_models.Account.CREDIT
            ),
        )
        self.last_transaction = models.Transaction.objects.create(
            amount=100,
            transaction_type=models.Transaction.TIERING_BONUS,
            account=self.user_1.accounts.get(
                account_type=account_models.Account.TIERING
            ),
        )
        user_models.User.objects.create(username="user_2")

    def test_get_admin_transactions(self):
        request = self.factory.get("/admin/transactions/")
        force_authenticate(request, self.auth_user)
        response = views.AdminTransactionAPIView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)

    def test_get_admin_transactions_filter(self):
        models.Transaction.objects.create(
            amount=100,
            transaction_type=models.Transaction.TRADING_BONUS,
            account=self.user_1.accounts.get(account_type=account_models.Account.TRADE),
        )
        params = {"account_type": account_models.Account.TRADE}
        request = self.factory.get("/admin/transactions/", params)
        force_authenticate(request, self.auth_user)
        response = views.AdminTransactionAPIView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        first = response.data["results"][0]
        self.assertEqual(models.Transaction.TRADING_BONUS, first["transaction_type"])
        self.assertEqual(self.user_1.id, first["user_id"])

    def test_get_admin_transaction_search(self):
        user = user_models.User.objects.get(username="user_2")
        models.Transaction.objects.create(
            amount=100,
            transaction_type=models.Transaction.ADMIN_TRANSACTION,
            account=user.accounts.get(account_type=account_models.Account.CREDIT),
        )
        params = {"search": "user_2"}
        request = self.factory.get("/admin/transactions/", params)
        force_authenticate(request, self.auth_user)
        response = views.AdminTransactionAPIView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        first = response.data["results"][0]
        self.assertEqual(user.id, first["user_id"])

    def test_get_admin_transactions_ordering(self):
        params = {"ordering": "-id"}
        request = self.factory.get("/admin/transactions/", params)
        force_authenticate(request, self.auth_user)
        response = views.AdminTransactionAPIView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        first = response.data["results"][0]
        self.assertEqual(self.last_transaction.id, first["id"])

    def test_post_admin_transaction(self):
        data = {
            "amount": 100,
            "transaction_type": models.Transaction.DEPOSIT_TRANSACTION,
            "account": self.user_1.accounts.get(
                account_type=account_models.Account.CREDIT
            ).id,
        }
        request = self.factory.post("/admin/transactions/", data)
        force_authenticate(request, self.auth_user)
        response = views.AdminTransactionAPIView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.user_1.id, response.data["user_id"])
        self.assertEqual(
            models.Transaction.DEPOSIT_TRANSACTION, response.data["transaction_type"]
        )

    def test_get_admin_transaction_details(self):
        request = self.factory.get("/admin/transactions/")
        force_authenticate(request, self.auth_user)
        response = views.AdminTransactionDetailsAPIView.as_view()(
            request, pk=self.last_transaction.id
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.last_transaction.id, response.data["id"])

    def test_patch_admin_transaction_details(self):
        data = {"transaction_status": models.Transaction.VOIDED, "remark": "Testing"}
        request = self.factory.patch("/admin/transactions/", data)
        force_authenticate(request, self.auth_user)
        response = views.AdminTransactionDetailsAPIView.as_view()(
            request, pk=self.last_transaction.id
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.last_transaction.id, response.data["id"])
        self.assertEqual(models.Transaction.VOIDED, response.data["transaction_status"])
        self.assertEqual("Testing", response.data["remark"])

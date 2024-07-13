from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate

from user import models as user_models

from account import tests as account_tests

from transaction import models as transaction_models

from withdrawal import models

from api_admin.withdrawal import views


class AdminWithdrawalAPITestCase(APITestCase):
    @account_tests.patch_task_account_create_new_user
    def setUp(self) -> None:
        self.factory = APIRequestFactory()
        self.auth_user = user_models.User.objects.create(
            username="admin", is_staff=True
        )
        self.user = user_models.User.objects.create(
            username="testuser",
        )

        self.account = self.user.accounts.get(account_type=1)
        self.blockchain_withdrawal = models.WithdrawalBlockchain.objects.create(
            wallet_address="test_address",
            withdrawal_transaction=transaction_models.Transaction.objects.create(
                amount=200,
                transaction_type=transaction_models.Transaction.WITHDRAWAL_TRANSACTION,
                account=self.account,
                transaction_status=transaction_models.Transaction.PENDING,
            ),
            service_fee_transaction=transaction_models.Transaction.objects.create(
                amount=20,
                transaction_type=transaction_models.Transaction.WITHDRAWAL_FEE,
                account=self.account,
            ),
            gas_fee_transaction=transaction_models.Transaction.objects.create(
                amount=10,
                transaction_type=transaction_models.Transaction.WITHDRAWAL_FEE,
                account=self.account,
            ),
        )
        models.WithdrawalBlockchain.objects.create(
            wallet_address="test_address",
            withdrawal_transaction=transaction_models.Transaction.objects.create(
                amount=200,
                transaction_type=transaction_models.Transaction.WITHDRAWAL_TRANSACTION,
                account=self.account,
                transaction_status=transaction_models.Transaction.VOIDED,
            ),
            service_fee_transaction=transaction_models.Transaction.objects.create(
                amount=20,
                transaction_type=transaction_models.Transaction.WITHDRAWAL_FEE,
                account=self.account,
            ),
            gas_fee_transaction=transaction_models.Transaction.objects.create(
                amount=10,
                transaction_type=transaction_models.Transaction.WITHDRAWAL_FEE,
                account=self.account,
            ),
        )

        self.bank_withdrawal = models.WithdrawalBank.objects.create(
            withdrawal_transaction=transaction_models.Transaction.objects.create(
                amount=200,
                transaction_type=transaction_models.Transaction.WITHDRAWAL_TRANSACTION,
                account=self.account,
                transaction_status=transaction_models.Transaction.PENDING,
            ),
            service_fee_transaction=transaction_models.Transaction.objects.create(
                amount=20,
                transaction_type=transaction_models.Transaction.WITHDRAWAL_FEE,
                account=self.account,
            ),
        )
        models.WithdrawalBank.objects.create(
            withdrawal_transaction=transaction_models.Transaction.objects.create(
                amount=200,
                transaction_type=transaction_models.Transaction.WITHDRAWAL_TRANSACTION,
                account=self.account,
                transaction_status=transaction_models.Transaction.VOIDED,
            ),
            service_fee_transaction=transaction_models.Transaction.objects.create(
                amount=20,
                transaction_type=transaction_models.Transaction.WITHDRAWAL_FEE,
                account=self.account,
            ),
        )

    def test_get_admin_withdrawal_settings(self):
        request = self.factory.get("/admin/withdrawals/settings/")
        force_authenticate(request, self.auth_user)
        response = views.AdminWithdrawalSettingsAPIView.as_view()(request)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertIn("results", response.data)

    def test_get_admin_withdrawal_settings_details(self):
        settings = models.WithdrawalSettings.objects.get(id=1)
        request = self.factory.get("/admin/withdrawals/settings/")
        force_authenticate(request, self.auth_user)
        response = views.AdminWithdrawalSettingsDetailsAPIView.as_view()(
            request, pk=settings.id
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(settings.settings_type, response.data["settings_type"])

    def test_patch_admin_withdrawal_settings_details(self):
        rate = 5
        data = {"rate": rate}
        settings = models.WithdrawalSettings.objects.get(id=1)
        request = self.factory.patch("/admin/withdrawals/settings/", data)
        force_authenticate(request, self.auth_user)
        response = views.AdminWithdrawalSettingsDetailsAPIView.as_view()(
            request, pk=settings.id
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(settings.settings_type, response.data["settings_type"])
        self.assertEqual(rate, response.data["rate"])

    def test_get_admin_withdrawal_blockchain(self):
        request = self.factory.get("/admin/withdrawals/blockchains/")
        force_authenticate(request, self.auth_user)
        response = views.AdminWithdrawalBlockchainAPIView.as_view()(request)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertIn("results", response.data)
        first = response.data["results"][0]
        self.assertEqual(self.blockchain_withdrawal.id, first["id"])
        self.assertEqual(
            self.blockchain_withdrawal.wallet_address, first["wallet_address"]
        )

    def test_get_admin_withdrawal_blockchain_search(self):
        params = {"search": "testuser"}
        request = self.factory.get("/admin/withdrawals/blockchains/", params)
        force_authenticate(request, self.auth_user)
        response = views.AdminWithdrawalBlockchainAPIView.as_view()(request)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertIn("results", response.data)
        first = response.data["results"][0]
        self.assertEqual(self.blockchain_withdrawal.id, first["id"])
        self.assertEqual(
            self.blockchain_withdrawal.wallet_address, first["wallet_address"]
        )

    def test_get_admin_withdrawal_blockchain_filter(self):
        params = {"withdrawal_status": transaction_models.Transaction.AUTHORIZED}
        request = self.factory.get("/admin/withdrawals/blockchains/", params)
        force_authenticate(request, self.auth_user)
        response = views.AdminWithdrawalBlockchainAPIView.as_view()(request)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertIn("results", response.data)
        self.assertEqual(0, len(response.data["results"]))

    def test_get_admin_withdrawal_blockchain_ordering(self):
        withdrawal = models.WithdrawalBlockchain.objects.all().order_by("-id").first()
        params = {"ordering": "-id"}
        request = self.factory.get("/admin/withdrawals/blockchains/", params)
        force_authenticate(request, self.auth_user)
        response = views.AdminWithdrawalBlockchainAPIView.as_view()(request)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertIn("results", response.data)
        first = response.data["results"][0]
        self.assertEqual(withdrawal.id, first["id"])

    def test_get_admin_withdrawal_blockchain_details(self):
        request = self.factory.get("/admin/withdrawals/blockchains/")
        force_authenticate(request, self.auth_user)
        response = views.AdminWithdrawalBlockchainDetailsAPIView.as_view()(
            request, pk=self.blockchain_withdrawal.id
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(self.blockchain_withdrawal.id, response.data["id"])

    def test_patch_admin_withdrawal_blockchain_details(self):
        data = {
            "withdrawal_transaction": {
                "id": self.blockchain_withdrawal.withdrawal_transaction.id,
                "transaction_status": transaction_models.Transaction.AUTHORIZED,
            },
        }
        request = self.factory.patch(
            "/admin/withdrawals/blockchains/", data=data, format="json"
        )
        force_authenticate(request, self.auth_user)
        response = views.AdminWithdrawalBlockchainDetailsAPIView.as_view()(
            request, pk=self.blockchain_withdrawal.id
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        self.blockchain_withdrawal.refresh_from_db()
        self.assertEqual(self.blockchain_withdrawal.id, response.data["id"])
        self.assertEqual(
            self.blockchain_withdrawal.withdrawal_transaction.transaction_status,
            transaction_models.Transaction.AUTHORIZED,
        )

    def test_get_admin_withdrawal_bank(self):
        request = self.factory.get("/admin/withdrawals/banks/")
        force_authenticate(request, self.auth_user)
        response = views.AdminWithdrawalBankAPIView.as_view()(request)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertIn("results", response.data)
        first = response.data["results"][0]
        self.assertEqual(self.bank_withdrawal.id, first["id"])

    def test_get_admin_withdrawal_bank_search(self):
        params = {"search": "testuser"}
        request = self.factory.get("/admin/withdrawals/banks/", params)
        force_authenticate(request, self.auth_user)
        response = views.AdminWithdrawalBankAPIView.as_view()(request)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertIn("results", response.data)
        first = response.data["results"][0]
        self.assertEqual(self.blockchain_withdrawal.id, first["id"])

    def test_get_admin_withdrawal_bank_filter(self):
        params = {"withdrawal_status": transaction_models.Transaction.AUTHORIZED}
        request = self.factory.get("/admin/withdrawals/bank/", params)
        force_authenticate(request, self.auth_user)
        response = views.AdminWithdrawalBankAPIView.as_view()(request)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertIn("results", response.data)
        self.assertEqual(0, len(response.data["results"]))

    def test_get_admin_withdrawal_bank_ordering(self):
        withdrawal = models.WithdrawalBank.objects.all().order_by("-id").first()
        params = {"ordering": "-id"}
        request = self.factory.get("/admin/withdrawals/banks/", params)
        force_authenticate(request, self.auth_user)
        response = views.AdminWithdrawalBlockchainAPIView.as_view()(request)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertIn("results", response.data)
        first = response.data["results"][0]
        self.assertEqual(withdrawal.id, first["id"])

    def test_get_admin_withdrawal_bank_details(self):
        request = self.factory.get("/admin/withdrawals/banks/")
        force_authenticate(request, self.auth_user)
        response = views.AdminWithdrawalBankDetailsAPIView.as_view()(
            request, pk=self.bank_withdrawal.id
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(self.bank_withdrawal.id, response.data["id"])

    def test_patch_admin_withdrawal_bank_details(self):
        data = {
            "withdrawal_transaction": {
                "id": self.bank_withdrawal.withdrawal_transaction.id,
                "transaction_status": transaction_models.Transaction.AUTHORIZED,
            },
        }
        request = self.factory.patch(
            "/admin/withdrawals/banks/", data=data, format="json"
        )
        force_authenticate(request, self.auth_user)
        response = views.AdminWithdrawalBankDetailsAPIView.as_view()(
            request, pk=self.bank_withdrawal.id
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        self.bank_withdrawal.refresh_from_db()
        self.assertEqual(self.bank_withdrawal.id, response.data["id"])
        self.assertEqual(
            self.bank_withdrawal.withdrawal_transaction.transaction_status,
            transaction_models.Transaction.AUTHORIZED,
        )

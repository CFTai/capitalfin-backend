from django.contrib import auth

from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate

from user import models as user_models

from account import tests as account_tests

from upload import models as upload_models

from bank import models as bank_models

from blockchain import models as blockchain_models

from transaction import models as transaction_models

from withdrawal import views, models


# Create your tests here.
class WithdrawalAPITestCase(APITestCase):
    @account_tests.patch_task_account_create_new_user
    def setUp(self) -> None:
        self.factory = APIRequestFactory()
        self.auth_user = user_models.User.objects.create(
            username="testuser",
            transaction_password=auth.hashers.make_password("P@ssw0rd"),
            status=user_models.User.VERIFIED,
        )

        attachment = upload_models.Upload.objects.create(file_data="test_path")
        blockchain_models.BlockchainWallet.objects.create(
            wallet_address="withdrawal_wallet_address",
            wallet_status=blockchain_models.BlockchainWallet.AUTHORIZED,
            user=self.auth_user,
            attachment=attachment,
        )

        self.account = self.auth_user.accounts.get(account_type=1)
        transaction_models.Transaction.objects.create(
            amount=200, transaction_type=1, account=self.account
        )
        return super().setUp()

    def test_post_withdrawal_quote(self):
        amount = 200
        data = {"account": "usdt", "amount": amount}
        request = self.factory.post("/withdrawal/quote/", data)
        force_authenticate(request, self.auth_user)
        response = views.WithdrawalQuotaAPIView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        service_fee = models.WithdrawalSettings.objects.get(
            settings_type=models.WithdrawalSettings.BLOCKCHAIN_SERVICE_FEE
        )
        service_fee = amount * service_fee.rate
        gas_fee = models.WithdrawalSettings.objects.get(
            settings_type=models.WithdrawalSettings.BLOCKCHAIN_GAS_FEE
        )
        self.assertEqual(gas_fee.rate, response.data["gas_fee"])
        self.assertEqual(service_fee, response.data["service_fee"])
        self.assertEqual(
            amount - gas_fee.rate - service_fee, response.data["total_amount"]
        )

    def test_post_withdrawal(self):
        amount = 200
        data = {"account": "usdt", "amount": amount, "transaction_password": "P@ssw0rd"}
        request = self.factory.post("/withdrawal/quote/", data)
        force_authenticate(request, self.auth_user)
        response = views.WithdrawalAPIView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        withdrawal_tx = transaction_models.Transaction.objects.get(
            account=self.account,
            transaction_type=transaction_models.Transaction.WITHDRAWAL_TRANSACTION,
        )
        withdrawal = models.WithdrawalBlockchain.objects.get(
            withdrawal_transaction=withdrawal_tx
        )

        service_fee = models.WithdrawalSettings.objects.get(
            settings_type=models.WithdrawalSettings.BLOCKCHAIN_SERVICE_FEE
        )
        service_fee = amount * service_fee.rate
        gas_fee = models.WithdrawalSettings.objects.get(
            settings_type=models.WithdrawalSettings.BLOCKCHAIN_GAS_FEE
        )

        self.assertEqual(gas_fee.rate * -1, withdrawal.gas_fee_transaction.amount)
        self.assertEqual(service_fee * -1, withdrawal.service_fee_transaction.amount)
        self.assertEqual(
            (amount - gas_fee.rate - service_fee) * -1, withdrawal_tx.amount
        )

    def test_post_bank_withdrawal(self):
        bank_models.Bank.objects.create(
            user=self.auth_user, bank_status=bank_models.Bank.AUTHORIZED
        )

        amount = 200
        data = {
            "account": "usdt",
            "amount": amount,
            "transaction_password": "P@ssw0rd",
            "method": "bank",
        }
        request = self.factory.post("/withdrawal/quote/", data)
        force_authenticate(request, self.auth_user)
        response = views.WithdrawalAPIView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        withdrawal_tx = transaction_models.Transaction.objects.get(
            account=self.account,
            transaction_type=transaction_models.Transaction.WITHDRAWAL_TRANSACTION,
        )
        withdrawal = models.WithdrawalBank.objects.get(
            withdrawal_transaction=withdrawal_tx
        )

        service_fee = models.WithdrawalSettings.objects.get(
            settings_type=models.WithdrawalSettings.BLOCKCHAIN_SERVICE_FEE
        )
        service_fee = amount * service_fee.rate

        self.assertEqual(service_fee * -1, withdrawal.service_fee_transaction.amount)
        self.assertEqual((amount - service_fee) * -1, withdrawal_tx.amount)

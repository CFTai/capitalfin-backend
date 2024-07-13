from django.contrib import auth

from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate

from user import models as user_models

from upload import models as upload_models

from blockchain import views, models


# Create your tests here.
class BlockchainAPITestCase(APITestCase):
    def setUp(self) -> None:
        self.factory = APIRequestFactory()
        self.auth_user = user_models.User.objects.create(
            username="testuser",
            transaction_password=auth.hashers.make_password("P@ssw0rd"),
        )
        attachment = upload_models.Upload.objects.create(file_data="test_path")
        self.wallet = models.BlockchainWallet.objects.create(
            user=self.auth_user, attachment=attachment
        )

    def test_get_blockchain_wallets(self):
        request = self.factory.get("/blockchain/wallets/")
        force_authenticate(request, self.auth_user)
        response = views.BlockchainWalletAPIView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        first = response.data["results"][0]
        self.assertEqual(first["id"], self.wallet.id)
        self.assertEqual(first["wallet_status"], models.BlockchainWallet.PENDING)

    def test_post_blockchain_wallets(self):
        attachment = upload_models.Upload.objects.create(file_data="test_path")
        data = {
            "transaction_password": "P@ssw0rd",
            "wallet_address": "new_address",
            "attachment": attachment.pk,
        }
        request = self.factory.post("/blockchain/wallets/", data)
        force_authenticate(request, self.auth_user)
        response = views.BlockchainWalletAPIView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["wallet_address"], "new_address")
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.wallet_status, models.BlockchainWallet.DEACTIVATED)

    def test_get_blockchain_wallet_details(self):
        models.BlockchainWallet.objects.filter(id=self.wallet.id).update(
            wallet_status=models.BlockchainWallet.AUTHORIZED
        )

        request = self.factory.get("/blockchain/wallets/")
        force_authenticate(request, self.auth_user)
        response = views.BlockchainWalletDetailsAPIView.as_view()(
            request, wallet_status=models.BlockchainWallet.WALLET_STATUS[1][1]
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.wallet.id)
        self.assertEqual(
            response.data["wallet_status"], models.BlockchainWallet.AUTHORIZED
        )

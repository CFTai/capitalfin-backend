from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate

from user import models as user_models

from upload import models as upload_models

from blockchain import models

from api_admin.blockchain import views


class AdminBlockchainAPITestCase(APITestCase):
    def setUp(self) -> None:
        self.factory = APIRequestFactory()
        self.auth_user = user_models.User.objects.create(
            username="admin", email="admin@unittest.com", is_staff=True
        )

        self.user = user_models.User.objects.create(username="user_1")
        models.BlockchainWallet.objects.create(
            user=self.user,
            wallet_address="address_1",
            attachment=upload_models.Upload.objects.create(file_data="test_path"),
            wallet_status=models.BlockchainWallet.DEACTIVATED,
        )
        self.wallet = models.BlockchainWallet.objects.create(
            user=self.user,
            wallet_address="address_2",
            attachment=upload_models.Upload.objects.create(file_data="test_path"),
            wallet_status=models.BlockchainWallet.AUTHORIZED,
        )

        self.user_2 = user_models.User.objects.create(username="user_2")
        models.BlockchainWallet.objects.create(
            user=self.user_2,
            wallet_address="address_1",
            attachment=upload_models.Upload.objects.create(file_data="test_path"),
            wallet_status=models.BlockchainWallet.AUTHORIZED,
        )

    def test_get_admin_blockchain_wallets(self):
        request = self.factory.get("/admin/blockchain/wallets/")
        force_authenticate(request, self.auth_user)
        response = views.AdminBlockchainWalletAPIView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        first = response.data["results"][0]
        self.assertEqual(first["wallet_address"], "address_1")

    def test_get_admin_blockchain_wallets_search(self):
        params = {"search": self.user.username}
        request = self.factory.get("/admin/blockchain/wallets/", params)
        force_authenticate(request, self.auth_user)
        response = views.AdminBlockchainWalletAPIView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertEqual(
            models.BlockchainWallet.objects.filter(user=self.user).count(),
            len(response.data["results"]),
        )

    def test_get_admin_blockchain_wallets_filter(self):
        params = {"wallet_status": models.BlockchainWallet.AUTHORIZED}
        request = self.factory.get("/admin/blockchain/wallets/", params)
        force_authenticate(request, self.auth_user)
        response = views.AdminBlockchainWalletAPIView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertEqual(
            models.BlockchainWallet.objects.filter(
                wallet_status=models.BlockchainWallet.AUTHORIZED
            ).count(),
            len(response.data["results"]),
        )

    def test_get_admin_blockchain_wallets_ordering(self):
        params = {"ordering": "-id"}
        request = self.factory.get("/admin/blockchain/wallets/", params)
        force_authenticate(request, self.auth_user)
        response = views.AdminBlockchainWalletAPIView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        last = models.BlockchainWallet.objects.order_by("-id").first()
        result = response.data["results"][0]
        self.assertEqual(last.id, result["id"])

    def test_get_admin_blockchain_wallet_details(self):
        request = self.factory.get("/admin/blockchain/wallets/")
        force_authenticate(request, self.auth_user)
        response = views.AdminBlockchainWalletDetailsAPIView.as_view()(
            request, pk=self.wallet.id
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.wallet.id)

    def test_patch_admin_blockchain_wallet_details(self):
        wallet = models.BlockchainWallet.objects.create(
            user=self.user,
            wallet_address="address_3",
            attachment=upload_models.Upload.objects.create(file_data="test_path"),
        )
        data = {"wallet_status": models.BlockchainWallet.AUTHORIZED}
        request = self.factory.patch("/admin/blockchain/wallets/", data)
        force_authenticate(request, self.auth_user)
        response = views.AdminBlockchainWalletDetailsAPIView.as_view()(
            request, pk=wallet.id
        )
        wallet.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], wallet.id)
        self.assertEqual(response.data["wallet_status"], wallet.wallet_status)

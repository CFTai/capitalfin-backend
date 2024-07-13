from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate

from user.models import User

from goldmine import models

from api_admin.goldmine import views


class AdminGoldmineAPITestCase(APITestCase):
    def setUp(self) -> None:
        self.factory = APIRequestFactory()
        self.auth_user = User.objects.create(username="admin", is_staff=True)

        user_1 = User.objects.create(username="user_1")
        user_2 = User.objects.create(username="user_2")

        bonus_transactions = [
            models.GoldmineBonusTransaction(
                total_invest_bonus=1000,
                level=1,
                bonus=10,
                user=user_1,
            ),
            models.GoldmineBonusTransaction(
                total_invest_bonus=1000,
                level=2,
                bonus=10,
                user=user_1,
            ),
            models.GoldmineBonusTransaction(
                total_invest_bonus=1000,
                level=1,
                bonus=10,
                user=user_2,
            ),
        ]
        models.GoldmineBonusTransaction.objects.bulk_create(bonus_transactions)

    def test_get_admin_goldmine_bonus_settings(self):
        request = self.factory.get("/admin/goldmine/settings/")
        force_authenticate(request, self.auth_user)
        response = views.AdminGoldmineBonusSettingsAPIView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)

    def test_get_admin_goldmine_bonus_settings_details(self):
        settings = models.GoldmineBonusSettings.objects.get(id=1)

        request = self.factory.get("/admin/goldmine/settings/")
        force_authenticate(request, self.auth_user)
        response = views.AdminGoldmineBonusSettingsDetailsAPIView.as_view()(
            request, pk=settings.id
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], settings.id)

    def test_patch_admin_goldmine_bonus_settings_details(self):
        settings = models.GoldmineBonusSettings.objects.get(id=1)
        data = {"rate": "0.1"}

        request = self.factory.patch("/admin/goldmine/settings/", data)
        force_authenticate(request, self.auth_user)
        response = views.AdminGoldmineBonusSettingsDetailsAPIView.as_view()(
            request, pk=settings.id
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        settings.refresh_from_db()
        self.assertEqual(response.data["id"], settings.id)
        self.assertEqual(response.data["rate"], settings.rate)

    def test_get_admin_goldmine_bonus_transactions(self):
        request = self.factory.get("/admin/goldmine/bonus/")
        force_authenticate(request, self.auth_user)
        response = views.AdminGoldmineBonusTransactionAPIView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)

    def test_get_admin_goldmine_bonus_transactions_search(self):
        transactions = models.GoldmineBonusTransaction.objects.filter(
            user__username="user_1"
        )

        params = {"search": "user_1"}
        request = self.factory.get("/admin/goldmine/bonus/", params)
        force_authenticate(request, self.auth_user)
        response = views.AdminGoldmineBonusTransactionAPIView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertEqual(len(response.data["results"]), transactions.count())

    def test_get_admin_goldmine_bonus_transactions_details(self):
        transaction = models.GoldmineBonusTransaction.objects.get(id=1)

        request = self.factory.get("/admin/goldmine/bonus/")
        force_authenticate(request, self.auth_user)
        response = views.AdminGoldmineBonusTransactionDetailsAPIView.as_view()(
            request, pk=transaction.id
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], transaction.id)
        self.assertEqual(response.data["bonus"], transaction.bonus)

    def test_patch_admin_goldmine_bonus_transactions_details(self):
        transaction = models.GoldmineBonusTransaction.objects.get(id=1)
        data = {"status": models.GoldmineBonusTransaction.VOIDED}

        request = self.factory.patch("/admin/goldmine/bonus/", data)
        force_authenticate(request, self.auth_user)
        response = views.AdminGoldmineBonusTransactionDetailsAPIView.as_view()(
            request, pk=transaction.id
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        transaction.refresh_from_db()
        self.assertEqual(response.data["id"], transaction.id)
        self.assertEqual(response.data["status"], transaction.status)

from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate

from user import models as user_models

from bank import models

from api_admin.bank import views


class AdminBankAPITestCase(APITestCase):
    def setUp(self) -> None:
        self.auth_user = user_models.User.objects.create(
            username="admin", email="admin@unittest.com", is_staff=True
        )

        self.user_1 = user_models.User.objects.create(
            username="user_1",
            email="user_1@unittest.com",
        )
        models.Bank.objects.create(
            account_name="test_user_1",
            user=self.user_1,
            bank_status=models.Bank.AUTHORIZED,
        )
        models.Bank.objects.create(
            account_name="test_user_1",
            user=self.user_1,
            bank_status=models.Bank.DEACTIVATED,
        )

        self.user_2 = user_models.User.objects.create(
            username="user_2",
            email="user_2@unittest.com",
        )
        models.Bank.objects.create(
            account_name="test_user_2",
            user=self.user_2,
            bank_status=models.Bank.DEACTIVATED,
        )

        self.factory = APIRequestFactory()

    def test_get_admin_banks(self):
        view = views.AdminBankAPIView.as_view()
        request = self.factory.get("/admin/banks/")
        force_authenticate(request, self.auth_user)
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)

    def test_get_admin_banks_search(self):
        params = {"search": "user_2"}
        view = views.AdminBankAPIView.as_view()
        request = self.factory.get("/admin/banks/", params)
        force_authenticate(request, self.auth_user)
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)

        first_result = response.data["results"][0]
        self.assertEqual(first_result["user"], self.user_2.id)
        self.assertEqual(first_result["account_name"], "test_user_2")

    def test_get_admin_bank_filter(self):
        params = {"bank_status": models.Bank.DEACTIVATED}
        view = views.AdminBankAPIView.as_view()
        request = self.factory.get("/admin/banks/", params)
        force_authenticate(request, self.auth_user)
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)

        total_deactivated = models.Bank.objects.filter(
            bank_status=models.Bank.DEACTIVATED
        ).count()
        self.assertEqual(len(response.data["results"]), total_deactivated)

    def test_get_admin_bank_ordering(self):
        params = {"ordering": "-id"}
        view = views.AdminBankAPIView.as_view()
        request = self.factory.get("/admin/banks/", params)
        force_authenticate(request, self.auth_user)
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)

        last_bank = models.Bank.objects.order_by("-id").first()
        first_result = response.data["results"][0]
        self.assertEqual(first_result["id"], last_bank.id)

    def test_get_admin_bank_details(self):
        bank = models.Bank.objects.create(account_name="test_user_2", user=self.user_2)

        view = views.AdminBankDetailsAPIView.as_view()
        request = self.factory.get("/admin/banks")
        force_authenticate(request, self.auth_user)
        response = view(request, pk=bank.pk)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], bank.id)

    def test_patch_admin_bank_details(self):
        bank = models.Bank.objects.create(account_name="test_user_2", user=self.user_2)
        data = {"bank_status": models.Bank.AUTHORIZED}

        view = views.AdminBankDetailsAPIView.as_view()
        request = self.factory.patch("/admin/banks", data)
        force_authenticate(request, self.auth_user)
        response = view(request, pk=bank.pk)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["bank_status"], models.Bank.AUTHORIZED)

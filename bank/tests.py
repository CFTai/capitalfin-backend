from django.contrib import auth

from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate

from user import models as user_models

from bank import models, views


# Create your tests here.
class BankAPITestCase(APITestCase):
    def setUp(self) -> None:
        self.auth_user = user_models.User.objects.create(
            username="testuser",
            email="test@unittest.com",
            transaction_password=auth.hashers.make_password("password"),
        )
        self.bank = models.Bank.objects.create(
            account_name="test_account_name",
            user=self.auth_user,
        )
        self.factory = APIRequestFactory()

    def test_get_banks(self):
        view = views.BankAPIView.as_view()
        request = self.factory.get("/banks/")
        force_authenticate(request, self.auth_user)
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        first_result = response.data["results"][0]
        self.assertEqual(first_result["bank_status"], models.Bank.PENDING)
        self.assertEqual(first_result["account_name"], "test_account_name")

    def test_post_banks(self):
        data = {
            "transaction_password": "password",
            "account_name": "new_account_name",
            "account_number": "new_account_number",
            "bank_name": "new_bank_name",
            "bank_country": "ABC",
            "bank_region": "new_bank_region",
            "bank_branch": "new_bank_branch",
        }

        view = views.BankAPIView.as_view()
        request = self.factory.post("/banks/", data)
        force_authenticate(request, self.auth_user)
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["bank_status"], models.Bank.PENDING)
        self.assertEqual(response.data["account_name"], "new_account_name")

        self.bank.refresh_from_db()
        self.assertEqual(self.bank.bank_status, models.Bank.DEACTIVATED)

    def test_get_bank_details(self):
        bank = models.Bank.objects.create(
            account_name="test_auth_account_name",
            bank_status=models.Bank.AUTHORIZED,
            user=self.auth_user,
        )
        view = views.BankDetailsAPIView.as_view()
        request = self.factory.get("/accounts/")
        force_authenticate(request, self.auth_user)
        response = view(request, bank_status="authorized")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], bank.id)
        self.assertEqual(response.data["bank_status"], models.Bank.AUTHORIZED)
        self.assertEqual(response.data["account_name"], "test_auth_account_name")

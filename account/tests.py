from unittest.mock import patch, Mock

from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate

from account import views, tasks

from user import models as user_models

patch_task_account_create_new_user = patch(
    "account.tasks.account_create_new_user.delay",
    Mock(wraps=tasks.account_create_new_user),
)

patch_task_account_update_available_balance = patch(
    "account.tasks.account_update_available_balance.delay",
    Mock(wraps=tasks.account_update_available_balance),
)


# Create your tests here.
class AccountAPITestCase(APITestCase):
    @patch_task_account_create_new_user
    def setUp(self) -> None:
        self.auth_user = user_models.User.objects.create(
            username="testuser",
            email="test@unittest.com",
        )
        self.factory = APIRequestFactory()

    def test_get_accounts(self):
        view = views.AccountAPIView.as_view()
        request = self.factory.get("/accounts/")
        force_authenticate(request, self.auth_user)
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_account_details(self):
        view = views.AccountDetailsAPIView.as_view()
        request = self.factory.get("/accounts/")
        force_authenticate(request, self.auth_user)
        response = view(request, account_type_display="usdt")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["account_type_display"], "usdt")

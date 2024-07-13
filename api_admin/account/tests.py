from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate

from user import models as user_models

from account import models, tests

from api_admin.account import views


class AdminAccountAPITestCase(APITestCase):
    @tests.patch_task_account_create_new_user
    def setUp(self) -> None:
        self.auth_user = user_models.User.objects.create(
            username="admin", email="admin@unittest.com", is_staff=True
        )
        user = user_models.User.objects.create(
            username="user_1",
            email="user@unittest.com",
        )

        self.factory = APIRequestFactory()

    def test_get_admin_accounts(self):
        view = views.AdminAccountAPIView.as_view()
        request = self.factory.get("/admin/accounts/")
        force_authenticate(request, self.auth_user)
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)

    def test_get_admin_accounts_search(self):
        # Search for not exist username
        params = {"search": "not_a_exist_username"}
        view = views.AdminAccountAPIView.as_view()
        request = self.factory.get("/admin/accounts/", params)
        force_authenticate(request, self.auth_user)
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Expect empty result
        self.assertListEqual(response.data["results"], [])

    def test_get_admin_accounts_filter(self):
        # Search username and filter with account_type
        params = {"search": "user_1", "account_type": models.Account.CREDIT}
        view = views.AdminAccountAPIView.as_view()
        request = self.factory.get("/admin/accounts/", params)
        force_authenticate(request, self.auth_user)
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        # Assert result a single record with expecting account type and username
        first_result = response.data["results"][0]
        self.assertEqual(first_result["account_type"], models.Account.CREDIT)
        self.assertEqual(first_result["username"], "user_1")

    def test_get_admin_accounts_ordering(self):
        # Ordering param, order account_type desc
        params = {"ordering": "-account_type"}
        view = views.AdminAccountAPIView.as_view()
        request = self.factory.get("/admin/accounts/", params)
        force_authenticate(request, self.auth_user)
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        # Assert the ordering result base on the LAST account type
        last_account_type = models.Account.ACCOUNT_TYPES[-1]
        first_result = response.data["results"][0]
        self.assertEqual(first_result["account_type"], last_account_type[0])

    def test_get_admin_account_details(self):
        account = models.Account.objects.all().first()
        view = views.AdminAccountDetailsAPIView.as_view()
        request = self.factory.get("/admin/accounts/")
        force_authenticate(request, self.auth_user)
        response = view(request, pk=account.pk)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], account.pk)

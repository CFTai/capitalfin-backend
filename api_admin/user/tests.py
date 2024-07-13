from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate

from user import models as user_models

from api_admin.user import views


class AdminUserAPITestCase(APITestCase):
    def setUp(self) -> None:
        self.auth_user = user_models.User.objects.create(
            username="admin", email="admin@unittest.com", is_staff=True
        )
        self.user = user_models.User.objects.create(
            username="user_1",
            email="user_1@unittest.com",
        )
        user_models.User.objects.create(
            username="user_2",
            email="user_2@unittest.com",
        )
        self.factory = APIRequestFactory()

    def test_get_admin_users(self):
        view = views.AdminUserAPIView.as_view()
        request = self.factory.get("/admin/users/")
        force_authenticate(request, self.auth_user)
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        results = response.data["results"]
        self.assertEqual(len(results), 2)

    def test_post_admin_users(self):
        data = {
            "username": "user_3",
            "first_name": "John",
            "last_name": "Doe",
            "email": "new_user@unittest.com",
            "password": "P@ssw0rd",
            "transaction_password": "P@ssw0rd",
        }
        view = views.AdminUserAPIView.as_view()
        request = self.factory.post("/admin/users/", data=data, format="json")
        force_authenticate(request, self.auth_user)
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_admin_user_details(self):
        view = views.AdminUserDetailsAPIView.as_view()
        request = self.factory.get("/admin/users/")
        force_authenticate(request, self.auth_user)
        response = view(request, pk=self.user.pk)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "user_1")

    def test_patch_admin_user_details(self):
        data = {
            "first_name": "Johnny",
        }
        view = views.AdminUserDetailsAPIView.as_view()
        request = self.factory.patch("/admin/users/", data=data, format="json")
        force_authenticate(request, self.auth_user)
        response = view(request, pk=self.user.pk)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["first_name"], "Johnny")

    def test_get_user_switch(self):
        view = views.AdminUserSwitchAPIView.as_view()
        request = self.factory.get("/admin/switch/")
        force_authenticate(request, self.auth_user)
        response = view(request, pk=self.user.pk)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("switch", response.data.keys())

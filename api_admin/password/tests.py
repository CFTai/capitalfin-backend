from django.contrib import auth

from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate

from user import models as user_models

from api_admin.password import views


class AdminPasswordAPITestCase(APITestCase):
    def setUp(self) -> None:
        self.auth_user = user_models.User.objects.create(
            username="admin", email="admin@unittest.com", is_staff=True
        )
        self.user = user_models.User.objects.create(
            username="user_1",
            email="user@unittest.com",
            password=auth.hashers.make_password("old_password"),
            transaction_password=auth.hashers.make_password("old_password"),
        )
        self.factory = APIRequestFactory()

    def test_get_admin_password_details(self):
        view = views.AdminPasswordDetailsAPIView.as_view()
        request = self.factory.get("/admin/passwords/")
        force_authenticate(request, self.auth_user)
        response = view(request, pk=self.user.pk)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "user_1")

    def test_put_admin_password_details(self):
        new_password = "new_password_123"
        data = {
            "username": "user_1",
            "password": new_password,
            "transaction_password": new_password,
        }
        view = views.AdminPasswordDetailsAPIView.as_view()
        request = self.factory.put("/admin/passwords/", data=data, format="json")
        force_authenticate(request, self.auth_user)
        response = view(request, pk=self.user.pk)

        self.user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(auth.hashers.check_password(new_password, self.user.password))
        self.assertTrue(
            auth.hashers.check_password(new_password, self.user.transaction_password)
        )

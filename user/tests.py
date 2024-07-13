from unittest.mock import patch, Mock

from django import utils
from django.contrib import auth

from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate

from referral import models as referral_models, tests as referral_tests

from user import models, views

from upload import models as upload_models


# Create your tests here.
class UserAPITestCase(APITestCase):
    def setUp(self):
        self.auth_user = models.User.objects.create(
            username="testuser",
            email="test@unittest.com",
            password=auth.hashers.make_password("old_password"),
        )
        self.referrer = models.User.objects.create(username="referrer")
        self.factory = APIRequestFactory()

    @patch("user.tasks.email_welcome_message.delay", Mock(return_value=None))
    def test_post_registration(self):
        data = {
            "username": "user_2",
            "first_name": "John",
            "last_name": "Doe",
            "email": "new_user@unittest.com",
            "password": "P@ssw0rd",
            "transaction_password": "P@ssw0rd",
        }

        view = views.RegistrationAPIView.as_view()
        request = self.factory.post("/users/", data=data, format="json")
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    @patch("user.tasks.email_welcome_message.delay", Mock(return_value=None))
    @referral_tests.patch_task_referral_registered
    def test_post_registration_referral(self):
        data = {
            "username": "user_3",
            "first_name": "John",
            "last_name": "Doe",
            "email": "new_user@unittest.com",
            "password": "P@ssw0rd",
            "transaction_password": "P@ssw0rd",
            "referrer_username": "referrer",
        }

        view = views.RegistrationAPIView.as_view()
        request = self.factory.post("/users/", data=data, format="json")
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(
            referral_models.Referral.objects.filter(referrer=self.referrer).first()
        )

    def test_get_profile(self):
        view = views.ProfileAPIView.as_view()
        request = self.factory.get("/users/profile/")
        force_authenticate(request, self.auth_user)
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_put_profile(self):
        # Mock uploaded file
        attachment_1 = upload_models.Upload.objects.create(file_data="test_path")
        attachment_2 = upload_models.Upload.objects.create(file_data="test_path")

        data = {
            "details": {
                "national_id": "9877456",
                "nationality": "USA",
                "date_of_birth": "1800-01-13",
                "gender": "M",
            },
            "contact": {
                "country": "USA",
                "address_1": "address line 1",
                "address_2": "address line 2",
                "country_code": "01",
                "contact_no": "145236987",
            },
            "attachments": [{"upload": attachment_1.pk}, {"upload": attachment_2.pk}],
        }

        view = views.ProfileAPIView.as_view()
        request = self.factory.put("/users/profile/", data=data, format="json")
        force_authenticate(request, self.auth_user)
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.auth_user.status, models.User.PENDING)
        self.assertTrue(hasattr(self.auth_user, "details"))
        self.assertTrue(hasattr(self.auth_user, "contact"))
        self.assertTrue(hasattr(self.auth_user, "attachments"))

    def test_post_password(self):
        new_password = "new_password_123"
        data = {
            "password_type": "login",
            "current_password": "old_password",
            "password": new_password,
            "confirm_password": new_password,
        }

        view = views.PasswordAPIView.as_view()
        request = self.factory.post("/users/password/", data=data, format="json")
        force_authenticate(request, self.auth_user)
        response = view(request)

        # Refresh the user from the database to get the updated password
        self.auth_user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            auth.hashers.check_password(new_password, self.auth_user.password)
        )

    @patch("user.tasks.email_forget_password.delay", Mock(return_value=None))
    def test_post_forget_password(self):
        data = {"username": "testuser"}

        view = views.ForgetPasswordAPIView.as_view()
        request = self.factory.post("/users/password/forget/", data=data, format="json")
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_reset_password(self):
        new_password = "new_password_321"

        force_byte = utils.encoding.force_bytes(self.auth_user.pk)
        uid = utils.http.urlsafe_base64_encode(force_byte)
        token = auth.tokens.default_token_generator.make_token(self.auth_user)

        data = {
            "uid": uid,
            "token": token,
            "password": new_password,
            "confirm_password": new_password,
        }

        view = views.ResetPasswordAPIView.as_view()
        request = self.factory.post("/users/password/reset/", data=data, format="json")
        response = view(request)

        # Refresh the user from the database to get the updated password
        self.auth_user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            auth.hashers.check_password(new_password, self.auth_user.password)
        )
        self.assertTrue(
            auth.hashers.check_password(
                new_password, self.auth_user.transaction_password
            )
        )

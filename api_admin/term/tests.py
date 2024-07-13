from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate

from user import models as user_models

from term import models

from api_admin.term import views


class AdminTermAPITestCase(APITestCase):
    def setUp(self) -> None:
        self.factory = APIRequestFactory()
        self.auth_user = user_models.User.objects.create(
            username="admin", is_staff=True
        )

    def test_get_admin_term_settings(self):
        request = self.factory.get("/admin/terms/settings/")
        force_authenticate(request, self.auth_user)
        response = views.AdminTermSettingsAPIView.as_view()(request)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertIn("results", response.data)
        count = models.TermSettings.objects.all().count()
        self.assertEqual(count, len(response.data["results"]))

    def test_get_admin_term_settings_details(self):
        settings = models.TermSettings.objects.get(id=1)
        request = self.factory.get("/admin/terms/settings/")
        force_authenticate(request, self.auth_user)
        response = views.AdminTermSettingsDetailsAPIView.as_view()(
            request, pk=settings.id
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(settings.id, response.data["id"])

    def test_patch_admin_term_settings_details(self):
        settings = models.TermSettings.objects.get(id=1)
        new_value = 2000
        data = {"value": new_value}
        request = self.factory.patch("/admin/terms/settings/", data)
        force_authenticate(request, self.auth_user)
        response = views.AdminTermSettingsDetailsAPIView.as_view()(
            request, pk=settings.id
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(settings.id, response.data["id"])
        self.assertEqual(new_value, response.data["value"])
        settings.refresh_from_db()
        self.assertEqual(new_value, settings.value)

    def test_get_admin_term(self):
        request = self.factory.get("/admin/terms/")
        force_authenticate(request, self.auth_user)
        response = views.AdminTermAPIView.as_view()(request)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertIn("results", response.data)
        count = models.Term.objects.all().count()
        self.assertEqual(count, len(response.data["results"]))

    def test_post_admin_term(self):
        days = 10
        data = {"title": "TEST term", "days": days}
        request = self.factory.post("/admin/terms/", data)
        force_authenticate(request, self.auth_user)
        response = views.AdminTermAPIView.as_view()(request)

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(days, response.data["days"])

    def test_get_admin_term_details(self):
        term = models.Term.objects.get(id=1)
        request = self.factory.get("/admin/terms/")
        force_authenticate(request, self.auth_user)
        response = views.AdminTermDetailsAPIView.as_view()(request, pk=term.id)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(term.id, response.data["id"])

    def test_patch_admin_term_details(self):
        term = models.Term.objects.get(id=1)
        days = 1000
        data = {"days": days}
        request = self.factory.patch("/admin/terms/", data)
        force_authenticate(request, self.auth_user)
        response = views.AdminTermDetailsAPIView.as_view()(request, pk=term.id)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(term.id, response.data["id"])
        self.assertEqual(days, response.data["days"])
        term.refresh_from_db()
        self.assertEqual(days, term.days)

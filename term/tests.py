from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate
from django.test import TestCase

from user import models as user_models
from term import views, models


# Create your tests here.
class TermSettingsTestCase(TestCase):
    def test_term_settings(self):
        term = models.TermSettings.objects.get(
            settings_type=models.TermSettings.MINIMUM_AMOUNT
        )
        self.assertEqual(term.value, 1000)

        term = models.TermSettings.objects.get(
            settings_type=models.TermSettings.AMOUNT_MULTIPLE
        )
        self.assertEqual(term.value, 10)

        term = models.TermSettings.objects.get(
            settings_type=models.TermSettings.EARLY_RENEWAL_DAYS
        )
        self.assertEqual(term.value, 30)

        term = models.TermSettings.objects.get(
            settings_type=models.TermSettings.SHARES_ALLOWANCE
        )
        self.assertEqual(term.value, 1)


class TermAPITestCase(APITestCase):
    def setUp(self) -> None:
        self.factory = APIRequestFactory()
        self.auth_user = user_models.User.objects.create(username="user_1")

    def test_get_terms(self):
        request = self.factory.get("/terms/")
        force_authenticate(request, self.auth_user)
        response = views.TermAPIView.as_view()(request)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertIn("results", response.data)
        total_records = models.Term.objects.all().count()
        self.assertEqual(total_records, len(response.data["results"]))

    def test_get_terms_filter(self):
        params = {"is_enable": False}
        request = self.factory.get("/terms/", params)
        force_authenticate(request, self.auth_user)
        response = views.TermAPIView.as_view()(request)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertIn("results", response.data)
        total_records = models.Term.objects.filter(is_enable=False).count()
        self.assertEqual(total_records, len(response.data["results"]))

    def test_get_terms_search(self):
        term = models.Term.objects.first()
        params = {"search": term.title}
        request = self.factory.get("/terms/", params)
        force_authenticate(request, self.auth_user)
        response = views.TermAPIView.as_view()(request)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertIn("results", response.data)
        result = response.data["results"][0]
        self.assertEqual(term.title, result["title"])

    def test_get_term_details(self):
        term = models.Term.objects.get(id=1)
        request = self.factory.get("/terms/")
        force_authenticate(request, self.auth_user)
        response = views.TermDetailsAPIView.as_view()(request, pk=term.id)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(term.id, response.data["id"])

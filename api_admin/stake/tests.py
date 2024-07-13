from django.utils import timezone

from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate

from user import models as user_models

from stake import models

from api_admin.stake import views


class AdminStakeAPITestCase(APITestCase):
    def setUp(self) -> None:
        self.factory = APIRequestFactory()
        self.auth_user = user_models.User.objects.create(
            username="admin", is_staff=True
        )

        self.user = user_models.User.objects.create(username="user_1")
        models.Stake.objects.create(
            amount=1000,
            total_amount=1000,
            start_date=timezone.now(),
            end_date=timezone.now(),
            user=self.user,
            term_id=1,
            stake_status=models.Stake.ACTIVE,
        )

        self.user_2 = user_models.User.objects.create(username="user_2")
        models.Stake.objects.create(
            amount=1000,
            total_amount=1000,
            start_date=timezone.now(),
            end_date=timezone.now(),
            user=self.user_2,
            term_id=2,
            stake_status=models.Stake.ACTIVE,
        )

    def test_get_admin_stakes(self):
        request = self.factory.get("/admin/stakes/")
        force_authenticate(request, self.auth_user)
        response = views.AdminStakeAPIView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        count = models.Stake.objects.all().count()
        self.assertEqual(count, len(response.data["results"]))

    def test_get_admin_stakes_search(self):
        params = {"search": "user_1"}
        request = self.factory.get("/admin/stakes/", params)
        force_authenticate(request, self.auth_user)
        response = views.AdminStakeAPIView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        stake = models.Stake.objects.filter(user=self.user).first()
        first = response.data["results"][0]
        self.assertEqual(stake.id, first["id"])

    def test_get_admin_stakes_filter(self):
        params = {"term": 1}
        request = self.factory.get("/admin/stakes/", params)
        force_authenticate(request, self.auth_user)
        response = views.AdminStakeAPIView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        stake = models.Stake.objects.filter(term_id=1).first()
        first = response.data["results"][0]
        self.assertEqual(stake.id, first["id"])

    def test_get_admin_stakes_ordering(self):
        params = {"ordering": "-id"}
        request = self.factory.get("/admin/stakes/", params)
        force_authenticate(request, self.auth_user)
        response = views.AdminStakeAPIView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        stake = models.Stake.objects.all().order_by("-id").first()
        first = response.data["results"][0]
        self.assertEqual(stake.id, first["id"])

    def test_get_admin_stake_details(self):
        stake = models.Stake.objects.all().order_by("-id").first()
        request = self.factory.get("/admin/stakes/")
        force_authenticate(request, self.auth_user)
        response = views.AdminStakeDetailsAPIView.as_view()(request, pk=stake.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(stake.id, response.data["id"])

    def test_patch_admin_stake_details(self):
        stake = models.Stake.objects.all().order_by("-id").first()
        data = {"stake_status": 4}
        request = self.factory.patch("/admin/stakes/", data)
        force_authenticate(request, self.auth_user)
        response = views.AdminStakeDetailsAPIView.as_view()(request, pk=stake.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        stake.refresh_from_db()
        self.assertEqual(stake.id, response.data["id"])
        self.assertEqual(4, response.data["stake_status"])

from django.contrib import auth
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate

from user import models as user_models
from account import models as account_models, tests as account_tests
from stake import views, models, tasks


# Create your tests here.
class StakeAPITestCase(APITestCase):
    @account_tests.patch_task_account_create_new_user
    def setUp(self) -> None:
        self.factory = APIRequestFactory()
        self.auth_user = user_models.User.objects.create(
            username="user",
            status=user_models.User.VERIFIED,
            transaction_password=auth.hashers.make_password("P@ssw0rd"),
        )

    def test_post_stake_quote(self):
        account_models.Account.objects.filter(
            account_type=account_models.Account.CREDIT, user=self.auth_user
        ).update(available_balance=1000)
        data = {"amount": 1000, "term": 1}
        request = self.factory.post("/stakes/quote/", data)
        force_authenticate(request, self.auth_user)
        response = views.StakeQuoteAPIView.as_view()(request)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(1000, response.data["amount"])

    def test_post_stake_quote_insufficient_balance(self):
        data = {"amount": 1000, "term": 1}
        request = self.factory.post("/stakes/quote/", data)
        force_authenticate(request, self.auth_user)
        response = views.StakeQuoteAPIView.as_view()(request)

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        error = response.data["amount"]
        self.assertEqual("Insufficient account balance.", error[0])

    def test_post_stake_quote_shares(self):
        account_models.Account.objects.filter(
            account_type=account_models.Account.SHARES, user=self.auth_user
        ).update(available_balance=1000)
        data = {"amount": 1000, "term": 1, "share_percentage": 100}
        request = self.factory.post("/stakes/quote/", data)
        force_authenticate(request, self.auth_user)
        response = views.StakeQuoteAPIView.as_view()(request)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(1000, response.data["amount"])

    def test_post_stake_quote_insufficient_shares(self):
        data = {"amount": 1000, "term": 1, "share_percentage": 100}
        request = self.factory.post("/stakes/quote/", data)
        force_authenticate(request, self.auth_user)
        response = views.StakeQuoteAPIView.as_view()(request)

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        error = response.data["share_percentage"]
        self.assertEqual("Insufficient account balance.", error[0])

    def test_post_stake_quote_active_stake(self):
        models.Stake.objects.create(
            amount=1,
            total_amount=1,
            start_date=timezone.now(),
            end_date=timezone.now(),
            user=self.auth_user,
            term_id=1,
            stake_status=models.Stake.ACTIVE,
        )
        account_models.Account.objects.filter(
            account_type=account_models.Account.CREDIT, user=self.auth_user
        ).update(available_balance=1000)
        data = {"amount": 1000, "term": 1}

        request = self.factory.post("/stakes/quote/", data)
        force_authenticate(request, self.auth_user)
        response = views.StakeQuoteAPIView.as_view()(request)

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        error = response.data["term"]
        self.assertEqual("Stake still active.", error[0])

    def test_post_stake_purchase(self):
        account_models.Account.objects.filter(
            account_type=account_models.Account.CREDIT, user=self.auth_user
        ).update(available_balance=1000)
        data = {"amount": 1000, "term": 1, "transaction_password": "P@ssw0rd"}
        request = self.factory.post("/stakes/quote/", data)
        force_authenticate(request, self.auth_user)
        response = views.StakeAPIView.as_view()(request)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        record = models.Stake.objects.get(
            user=self.auth_user, stake_status=models.Stake.ACTIVE
        )
        self.assertIsInstance(record, models.Stake)

    def test_post_stake_purchase_shares(self):
        account_models.Account.objects.filter(
            account_type=account_models.Account.SHARES, user=self.auth_user
        ).update(available_balance=1000)
        data = {
            "amount": 1000,
            "term": 1,
            "share_percentage": 100,
            "transaction_password": "P@ssw0rd",
        }
        request = self.factory.post("/stakes/", data)
        force_authenticate(request, self.auth_user)
        response = views.StakeAPIView.as_view()(request)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        record = models.Stake.objects.get(
            user=self.auth_user, stake_status=models.Stake.ACTIVE
        )
        self.assertIsInstance(record, models.Stake)

    def test_get_stake_details(self):
        stake = models.Stake.objects.create(
            amount=1,
            total_amount=1,
            start_date=timezone.now(),
            end_date=timezone.now(),
            user=self.auth_user,
            term_id=1,
            stake_status=models.Stake.ACTIVE,
        )
        view = views.StakeDetailsAPIView.as_view()
        request = self.factory.get("/stakes/")
        force_authenticate(request, self.auth_user)
        response = view(request, stake_status="active")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], stake.id)
        self.assertEqual(response.data["stake_status"], models.Stake.ACTIVE)

    def test_task_stake_status_update(self):
        stake_1 = models.Stake.objects.create(
            amount=1,
            total_amount=1,
            start_date=timezone.now(),
            end_date=timezone.now(),
            user=self.auth_user,
            term_id=1,
            stake_status=models.Stake.ACTIVE,
        )
        stake_2 = models.Stake.objects.create(
            amount=1,
            total_amount=1,
            start_date=timezone.now(),
            end_date=timezone.now() + timezone.timedelta(days=30),
            user=self.auth_user,
            term_id=1,
            stake_status=models.Stake.ACTIVE,
        )
        stake_3 = models.Stake.objects.create(
            amount=1,
            total_amount=1,
            start_date=timezone.now(),
            end_date=timezone.now() + timezone.timedelta(days=29),
            user=self.auth_user,
            term_id=1,
            stake_status=models.Stake.ACTIVE,
        )
        stake_4 = models.Stake.objects.create(
            amount=1,
            total_amount=1,
            start_date=timezone.now(),
            end_date=timezone.now() + timezone.timedelta(days=31),
            user=self.auth_user,
            term_id=1,
            stake_status=models.Stake.ACTIVE,
        )
        tasks.stake_status_update()

        stake_1.refresh_from_db()
        self.assertEqual(models.Stake.EXPIRED, stake_1.stake_status)

        stake_2.refresh_from_db()
        self.assertEqual(models.Stake.EXPIRING, stake_2.stake_status)

        stake_3.refresh_from_db()
        self.assertEqual(models.Stake.EXPIRING, stake_3.stake_status)

        stake_4.refresh_from_db()
        self.assertEqual(models.Stake.ACTIVE, stake_4.stake_status)

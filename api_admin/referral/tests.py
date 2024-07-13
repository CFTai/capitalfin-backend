from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate

from user import models as user_models

from account import tests as account_test

from referral import models

from api_admin.referral import views


class AdminReferralAPIViewTestCase(APITestCase):
    @account_test.patch_task_account_create_new_user
    def setUp(self) -> None:
        self.factory = APIRequestFactory()
        self.auth_user = user_models.User.objects.create(
            username="admin", is_staff=True
        )

        self.referrer = user_models.User.objects.create(username="referrer")
        referred_1 = user_models.User.objects.create(username="referred_1")
        fake_referrer = user_models.User.objects.create(username="fake")
        fake_referred_1 = user_models.User.objects.create(username="fake_1")

        self.referral = models.Referral.objects.create(
            referrer=self.referrer, referred=referred_1
        )
        transactions = [
            models.ReferralBonusTransaction(
                referrer_id=self.referrer.id,
                term_id=1,
                user_id=referred_1.id,
                amount=1000,
                rate=0.1,
                bonus=100,
            ),
            models.ReferralBonusTransaction(
                referrer_id=self.referrer.id,
                term_id=1,
                user_id=referred_1.id,
                amount=1000,
                rate=0.1,
                bonus=100,
            ),
            models.ReferralBonusTransaction(
                referrer_id=self.referrer.id,
                term_id=1,
                user_id=referred_1.id,
                amount=3000,
                rate=0.1,
                bonus=300,
            ),
            models.ReferralBonusTransaction(
                referrer_id=fake_referrer.id,
                term_id=1,
                user_id=fake_referred_1.id,
                amount=3000,
                rate=0.1,
                bonus=300,
            ),
        ]
        models.ReferralBonusTransaction.objects.bulk_create(transactions)

    def test_admin_get_referrals(self):
        request = self.factory.get("/admin/referrals/")
        force_authenticate(request, self.auth_user)
        response = views.AdminReferralAPIView.as_view()(request)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertIn("results", response.data)
        record = response.data["results"][0]
        self.assertEqual(self.referral.id, record["id"])
        self.assertEqual(self.referral.referrer.id, record["referrer"])
        self.assertEqual(self.referral.referred.id, record["referred"])

    def test_admin_get_search_referrals(self):
        params = {"search": "referrer"}
        request = self.factory.get("/admin/referrals/", params)
        force_authenticate(request, self.auth_user)
        response = views.AdminReferralAPIView.as_view()(request)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertIn("results", response.data)
        record = response.data["results"][0]
        self.assertEqual(self.referral.id, record["id"])
        self.assertEqual(self.referral.referrer.id, record["referrer"])
        self.assertEqual(self.referral.referred.id, record["referred"])

    def test_admin_post_referrals(self):
        referred_2 = user_models.User.objects.create(username="referred_2")
        data = {
            "referrer": self.referrer.id,
            "referred": referred_2.id,
        }
        request = self.factory.post("/admin/referrals/", data=data, format="json")
        force_authenticate(request, self.auth_user)
        response = views.AdminReferralAPIView.as_view()(request)

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(self.referrer.id, response.data["referrer"])
        self.assertEqual(referred_2.id, response.data["referred"])

    def test_admin_get_referral_details(self):
        request = self.factory.get("/admin/referrals/")
        force_authenticate(request, self.auth_user)
        response = views.AdminReferralDetailsAPIView.as_view()(
            request, pk=self.referral.id
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(self.referral.id, response.data["id"])
        self.assertEqual(self.referral.referrer.id, response.data["referrer"])
        self.assertEqual(self.referral.referred.id, response.data["referred"])

    def test_admin_patch_referral_details(self):
        referred_3 = user_models.User.objects.create(username="referred_3")
        data = {
            "referred": referred_3.id,
        }
        request = self.factory.patch("/admin/referrals/", data=data, format="json")
        force_authenticate(request, self.auth_user)

        response = views.AdminReferralDetailsAPIView.as_view()(
            request, pk=self.referral.id
        )
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(self.referral.id, response.data["id"])
        self.assertEqual(self.referral.referrer.id, response.data["referrer"])
        self.assertEqual(referred_3.id, response.data["referred"])

    def test_admin_get_referral_bonus_settings(self):
        request = self.factory.get("/admin/referrals/bonus/settings/")
        force_authenticate(request, self.auth_user)
        response = views.AdminReferralBonusSettingsAPIView.as_view()(request)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertIn("results", response.data)

    def test_admin_get_referral_bonus_settings_details(self):
        settings = models.ReferralBonusSettings.objects.get(id=1)
        request = self.factory.get("/admin/referrals/bonus/settings/")
        force_authenticate(request, self.auth_user)
        response = views.AdminReferralBonusSettingsDetailsAPIView.as_view()(
            request, pk=settings.id
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(settings.id, response.data["id"])
        self.assertEqual(settings.rate, response.data["rate"])

    def test_admin_patch_referral_bonus_settings_details(self):
        rate = 5
        data = {"rate": rate}
        settings = models.ReferralBonusSettings.objects.get(id=1)
        request = self.factory.get("/admin/referrals/bonus/settings/", data)
        force_authenticate(request, self.auth_user)
        response = views.AdminReferralBonusSettingsDetailsAPIView.as_view()(
            request, pk=settings.id
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        settings.refresh_from_db()
        self.assertEqual(settings.id, response.data["id"])
        self.assertEqual(settings.rate, response.data["rate"])

    def test_admin_get_referral_bonus_transactions(self):
        request = self.factory.get("/admin/referrals/bonus/")
        force_authenticate(request, self.auth_user)
        response = views.AdminReferralBonusTransactionAPIView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_get_referral_bonus_transactions_search(self):
        params = {"search": "referrer"}
        request = self.factory.get("/admin/referrals/bonus/", params)
        total_transaction = models.ReferralBonusTransaction.objects.filter(
            referrer=self.referrer
        )
        force_authenticate(request, self.auth_user)
        response = views.AdminReferralBonusTransactionAPIView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(total_transaction.count(), len(response.data["results"]))

    def test_admin_get_referral_bonus_transactions_details(self):
        transaction = models.ReferralBonusTransaction.objects.filter().first()
        request = self.factory.get("/admin/referrals/bonus/")
        force_authenticate(request, self.auth_user)
        response = views.AdminReferralBonusTransactionDetailsAPIView.as_view()(
            request, pk=transaction.id
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(transaction.id, response.data["id"])

    def test_admin_patch_referral_bonus_transactions_details(self):
        patch_status = models.ReferralBonusTransaction.VOIDED
        data = {"status": patch_status}
        transaction = models.ReferralBonusTransaction.objects.filter().first()
        request = self.factory.patch("/admin/referrals/bonus/", data)
        force_authenticate(request, self.auth_user)
        response = views.AdminReferralBonusTransactionDetailsAPIView.as_view()(
            request, pk=transaction.id
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        transaction.refresh_from_db()
        self.assertEqual(transaction.status, patch_status)

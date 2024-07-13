from django.utils import timezone

from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate

from user import models as user_models

from contract import views, models, tasks


# Create your tests here.
class ContractTestCase(APITestCase):
    def setUp(self) -> None:
        self.factory = APIRequestFactory()
        self.auth_user = user_models.User.objects.create(username="user_1")

        self.contract = models.Contract.objects.create(
            title="Contract 1",
            term_id=1,
            contract_status=models.Contract.OPEN,
            roi_rate_from=0.0025,
            roi_rate_to=0.0030,
        )
        models.Contract.objects.create(
            title="Contract 2", term_id=2, contract_status=models.Contract.CLOSED
        )
        models.Contract.objects.create(
            title="Contract 3",
            code="ABC",
            term_id=2,
            roi_rate_from=0.0005,
            roi_rate_to=0.001,
            contract_status=models.Contract.OPEN,
        )

    def test_get_contracts(self):
        request = self.factory.get("/contracts/")
        force_authenticate(request, self.auth_user)
        response = views.ContractAPIView.as_view()(request)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertIn("results", response.data)

    def test_get_contracts_filter(self):
        params = {"term": 2, "contract_status": models.Contract.OPEN}
        request = self.factory.get("/contracts/", params)
        force_authenticate(request, self.auth_user)
        response = views.ContractAPIView.as_view()(request)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertIn("results", response.data)
        contract = models.Contract.objects.filter(
            term=2, contract_status=models.Contract.OPEN
        ).first()
        result = response.data["results"][0]
        self.assertEqual(contract.id, result["id"])

    def test_get_contracts_search(self):
        params = {"search": "Contract 3"}
        request = self.factory.get("/contracts/", params)
        force_authenticate(request, self.auth_user)
        response = views.ContractAPIView.as_view()(request)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertIn("results", response.data)
        contract = models.Contract.objects.filter(title="Contract 3").first()
        result = response.data["results"][0]
        self.assertEqual(contract.id, result["id"])

    def test_get_contract_details(self):
        request = self.factory.get("/contracts/")
        force_authenticate(request, self.auth_user)
        response = views.ContractDetailsAPIView.as_view()(request, pk=self.contract.id)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(self.contract.id, response.data["id"])

    def test_task_contract_roi_generator(self):
        tasks.contract_roi_generator()

        roi_log = models.ContractRoiLog.objects.filter(contract=self.contract).first()
        self.assertTrue(
            self.contract.roi_rate_from <= roi_log.roi_rate <= self.contract.roi_rate_to
        )
        self.assertEqual(self.contract.roi_daily_rate, 0)
        self.contract.refresh_from_db()
        self.assertEqual(self.contract.roi_daily_rate, roi_log.roi_rate)

from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate

from user import models as user_models

from contract import models

from api_admin.contract import views


class AdminContractAPITestCase(APITestCase):
    def setUp(self) -> None:
        self.factory = APIRequestFactory()
        self.auth_user = user_models.User.objects.create(
            username="admin", is_staff=True
        )
        self.contract = models.Contract.objects.create(
            title="Contract 1", term_id=1, contract_status=models.Contract.OPEN
        )
        models.Contract.objects.create(
            title="Contract 2", term_id=2, contract_status=models.Contract.CLOSED
        )
        models.Contract.objects.create(
            title="Contract 3",
            code="ABC",
            term_id=2,
            contract_status=models.Contract.OPEN,
        )

    def test_get_admin_contracts(self):
        request = self.factory.get("/admin/contracts/")
        force_authenticate(request, self.auth_user)
        response = views.AdminContractAPIView.as_view()(request)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertIn("results", response.data)

    def test_get_admin_contracts_filter(self):
        params = {"term": 2, "contract_status": models.Contract.OPEN}
        request = self.factory.get("/admin/contracts/", params)
        force_authenticate(request, self.auth_user)
        response = views.AdminContractAPIView.as_view()(request)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertIn("results", response.data)
        contract = models.Contract.objects.filter(
            term=2, contract_status=models.Contract.OPEN
        ).first()
        result = response.data["results"][0]
        self.assertEqual(contract.id, result["id"])

    def test_get_admin_contracts_search(self):
        params = {"search": "Contract 3"}
        request = self.factory.get("/admin/contracts/", params)
        force_authenticate(request, self.auth_user)
        response = views.AdminContractAPIView.as_view()(request)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertIn("results", response.data)
        contract = models.Contract.objects.filter(title="Contract 3").first()
        result = response.data["results"][0]
        self.assertEqual(contract.id, result["id"])

    def test_post_admin_contract(self):
        data = {"title": "Contract 4", "term": 3}
        request = self.factory.post("/admin/contracts/", data)
        force_authenticate(request, self.auth_user)
        response = views.AdminContractAPIView.as_view()(request)

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

    def test_get_admin_contract_details(self):
        request = self.factory.get("/admin/contracts/")
        force_authenticate(request, self.auth_user)
        response = views.AdminContractDetailsAPIView.as_view()(
            request, pk=self.contract.id
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(self.contract.id, response.data["id"])

    def test_patch_admin_contract_details(self):
        data = {"contract_status": models.Contract.SUSPENDED}
        request = self.factory.patch("/admin/contracts/", data)
        force_authenticate(request, self.auth_user)
        response = views.AdminContractDetailsAPIView.as_view()(
            request, pk=self.contract.id
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(self.contract.id, response.data["id"])
        self.contract.refresh_from_db()
        self.assertEqual(self.contract.contract_status, models.Contract.SUSPENDED)

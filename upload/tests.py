from django.core.files.uploadedfile import SimpleUploadedFile

from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory

from upload import views


# Create your tests here.
class UploadAPITestCase(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    def test_post_upload(self):
        file_value = "Test file with size with 5MB."
        # Convert String to byte and calculate for 5MB file content
        file_content = file_value.encode("utf-8") * (5 * 1024 * 1024 // len(file_value))

        file_upload = SimpleUploadedFile(
            "test.jpg", file_content, content_type="text/plain"
        )

        view = views.UploadAPIView.as_view()
        request = self.factory.post(
            "/upload/", {"file_data": file_upload}, format="multipart"
        )
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

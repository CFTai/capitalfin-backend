from django import urls

from . import views

urlpatterns = [urls.path("", views.UploadAPIView.as_view(), name="upload")]

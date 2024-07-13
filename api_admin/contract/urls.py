from django import urls

from api_admin.contract import views

urlpatterns = [
    urls.path("", views.AdminContractAPIView.as_view()),
    urls.path("<int:pk>/", views.AdminContractDetailsAPIView.as_view()),
]

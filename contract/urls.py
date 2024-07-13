from django import urls

from contract import views

urlpatterns = [
    urls.path("", views.ContractAPIView.as_view(), name="contracts"),
    urls.path(
        "<int:pk>/", views.ContractDetailsAPIView.as_view(), name="contract details"
    ),
]

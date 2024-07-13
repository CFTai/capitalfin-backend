from django import urls

from api_admin.bank import views

urlpatterns = [
    urls.path("", views.AdminBankAPIView.as_view(), name="admin banks"),
    urls.path(
        "<int:pk>/", views.AdminBankDetailsAPIView.as_view(), name="admin bank details"
    ),
]

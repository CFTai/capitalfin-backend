from django import urls

from api_admin.transaction import views

urlpatterns = [
    urls.path("", views.AdminTransactionAPIView.as_view(), name="admin transactions"),
    urls.path(
        "<int:pk>/",
        views.AdminTransactionDetailsAPIView.as_view(),
        name="admin transaction details",
    ),
]

from django import urls

from transaction import views

urlpatterns = [
    urls.path("", views.TransactionAPIView.as_view(), name="transactions"),
    urls.path(
        "<int:pk>/",
        views.TransactionDetailsAPIView.as_view(),
        name="transaction details",
    ),
]

from django import urls

from withdrawal import views

urlpatterns = [
    urls.path("", views.WithdrawalAPIView.as_view(), name="withdrawal"),
    urls.path(
        "quote/", views.WithdrawalQuotaAPIView.as_view(), name="withdrawal quote"
    ),
]

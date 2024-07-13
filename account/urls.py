from django import urls

from account import views

urlpatterns = [
    urls.path("", views.AccountAPIView.as_view(), name="accounts"),
    urls.path(
        "<str:account_type_display>/",
        views.AccountDetailsAPIView.as_view(),
        name="account details",
    ),
]

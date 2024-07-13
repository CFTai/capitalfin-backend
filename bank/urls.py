from django import urls

from bank import views

urlpatterns = [
    urls.path("", views.BankAPIView.as_view(), name="banks"),
    urls.path(
        "<str:bank_status>/", views.BankDetailsAPIView.as_view(), name="bank details"
    ),
]

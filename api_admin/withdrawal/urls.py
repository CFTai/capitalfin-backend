from django import urls

from api_admin.withdrawal import views

urlpatterns = [
    urls.path(
        "settings/",
        views.AdminWithdrawalSettingsAPIView.as_view(),
        name="withdrawal settings",
    ),
    urls.path(
        "settings/<int:pk>/",
        views.AdminWithdrawalSettingsDetailsAPIView.as_view(),
        name="withdrawal settings details",
    ),
    urls.path(
        "blockchains/",
        views.AdminWithdrawalBlockchainAPIView.as_view(),
        name="withdrawal blockchain",
    ),
    urls.path(
        "blockchains/<int:pk>/",
        views.AdminWithdrawalBlockchainDetailsAPIView.as_view(),
        name="withdrawal blockchain details",
    ),
    urls.path(
        "banks/",
        views.AdminWithdrawalBankAPIView.as_view(),
        name="withdrawal bank",
    ),
    urls.path(
        "banks/<int:pk>/",
        views.AdminWithdrawalBankDetailsAPIView.as_view(),
        name="withdrawal bank details",
    ),
]

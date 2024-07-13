from django import urls

from api_admin.blockchain import views

urlpatterns = [
    urls.path(
        "wallets/", views.AdminBlockchainWalletAPIView.as_view(), name="admin wallets"
    ),
    urls.path(
        "wallets/<int:pk>/",
        views.AdminBlockchainWalletDetailsAPIView.as_view(),
        name="admin wallet details",
    ),
]

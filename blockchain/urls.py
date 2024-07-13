from django import urls

from blockchain import views

urlpatterns = [
    urls.path(
        "wallets/", views.BlockchainWalletAPIView.as_view(), name="blockchain wallets"
    ),
    urls.path(
        "wallets/<str:wallet_status>/",
        views.BlockchainWalletDetailsAPIView.as_view(),
        name="blockchain wallet details",
    ),
]

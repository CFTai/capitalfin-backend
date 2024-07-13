from django import urls

from rest_framework_simplejwt import views as jwt_views

urlpatterns = [
    urls.path(
        "token/",
        jwt_views.TokenObtainPairView.as_view(),
        name="admin-token-obtain-pair",
    ),
    urls.path("users/", urls.include("api_admin.user.urls")),
    urls.path("referrals/", urls.include("api_admin.referral.urls")),
    urls.path("passwords/", urls.include("api_admin.password.urls")),
    urls.path("accounts/", urls.include("api_admin.account.urls")),
    urls.path("banks/", urls.include("api_admin.bank.urls")),
    urls.path("transactions/", urls.include("api_admin.transaction.urls")),
    urls.path("blockchain/", urls.include("api_admin.blockchain.urls")),
    urls.path("withdrawals/", urls.include("api_admin.withdrawal.urls")),
    urls.path("terms/", urls.include("api_admin.term.urls")),
    urls.path("stakes/", urls.include("api_admin.stake.urls")),
    urls.path("contracts/", urls.include("api_admin.contract.urls")),
    urls.path("invests/", urls.include("api_admin.invest.urls")),
    urls.path("goldmine/", urls.include("api_admin.goldmine.urls")),
]

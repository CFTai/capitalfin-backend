from django import urls

from api_admin.referral import views

urlpatterns = [
    urls.path("", view=views.AdminReferralAPIView.as_view(), name="admin referrals"),
    urls.path(
        "<int:pk>/",
        view=views.AdminReferralDetailsAPIView.as_view(),
        name="admin referral details",
    ),
    urls.path(
        "bonus/settings/",
        view=views.AdminReferralBonusSettingsAPIView.as_view(),
        name="admin referral bonus settings",
    ),
    urls.path(
        "bonus/settings/<int:pk>/",
        view=views.AdminReferralBonusSettingsDetailsAPIView.as_view(),
        name="admin referral bonus settings",
    ),
    urls.path(
        "bonus/",
        view=views.AdminReferralBonusTransactionAPIView.as_view(),
        name="admin referral bonus transactions",
    ),
    urls.path(
        "bonus/<int:pk>/",
        view=views.AdminReferralBonusTransactionDetailsAPIView.as_view(),
        name="admin referral bonus transactions",
    ),
]

from django import urls

from referral import views

urlpatterns = [
    urls.path("", views.ReferralNetworkAPIView.as_view(), name="referral network")
]

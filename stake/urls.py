from django import urls

from stake import views

urlpatterns = [
    urls.path("", views.StakeAPIView.as_view(), name="stakes"),
    urls.path("quote/", views.StakeQuoteAPIView.as_view(), name="stake quote"),
    urls.path(
        "<str:stake_status>/", views.StakeDetailsAPIView.as_view(), name="stake details"
    ),
]

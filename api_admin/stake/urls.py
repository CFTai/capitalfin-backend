from django import urls

from api_admin.stake import views

urlpatterns = [
    urls.path("", views.AdminStakeAPIView.as_view(), name="admin stakes"),
    urls.path(
        "<int:pk>/",
        views.AdminStakeDetailsAPIView.as_view(),
        name="admin stake details",
    ),
]

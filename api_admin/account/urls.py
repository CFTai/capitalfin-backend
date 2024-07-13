from django import urls

from api_admin.account import views

urlpatterns = [
    urls.path("", views.AdminAccountAPIView.as_view(), name="admin accounts"),
    urls.path(
        "<int:pk>/",
        views.AdminAccountDetailsAPIView.as_view(),
        name="admin account details",
    ),
]

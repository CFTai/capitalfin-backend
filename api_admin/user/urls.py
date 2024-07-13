from django import urls

from . import views

urlpatterns = [
    urls.path("", views.AdminUserAPIView.as_view(), name="admin users"),
    urls.path(
        "switch/<int:pk>/",
        views.AdminUserSwitchAPIView.as_view(),
        name="admin user switch",
    ),
    urls.path(
        "<int:pk>/", views.AdminUserDetailsAPIView.as_view(), name="admin user details"
    ),
]

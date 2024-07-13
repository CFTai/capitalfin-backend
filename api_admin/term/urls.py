from django import urls

from api_admin.term import views

urlpatterns = [
    urls.path("", views.AdminTermAPIView.as_view(), name="admin terms"),
    urls.path(
        "<int:pk>/", views.AdminTermDetailsAPIView.as_view(), name="admin term details"
    ),
    urls.path(
        "settings/",
        views.AdminTermSettingsAPIView.as_view(),
        name="admin term settings",
    ),
    urls.path(
        "settings/<int:pk>/",
        views.AdminTermSettingsDetailsAPIView.as_view(),
        name="admin term settings details",
    ),
]

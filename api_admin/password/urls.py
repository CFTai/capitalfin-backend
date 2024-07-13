from django import urls

from . import views

urlpatterns = [
    urls.path(
        "<int:pk>/", views.AdminPasswordDetailsAPIView.as_view(), name="admin password"
    ),
]

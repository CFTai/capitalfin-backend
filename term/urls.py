from django import urls

from term import views

urlpatterns = [
    urls.path("", views.TermAPIView.as_view(), name="terms"),
    urls.path("<int:pk>/", views.TermDetailsAPIView.as_view(), name="term details"),
]

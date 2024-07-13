from django import urls

from invest import views

urlpatterns = [
    urls.path("", views.InvestAPIView.as_view()),
    urls.path("quote/", views.InvestQuoteAPIView.as_view(), name="invest quote"),
    urls.path("<int:pk>/", views.InvestDetailsAPIView.as_view()),
]

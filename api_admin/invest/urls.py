from django import urls

from api_admin.invest import views

urlpatterns = [
    urls.path("", views.AdminInvestAPIView.as_view()),
    urls.path("<int:pk>/", views.AdminInvestDetailsAPIView.as_view()),
    urls.path("bonus/", views.AdminInvestBonusTransactionAPIView.as_view()),
    urls.path("bonus/<int:pk>/", views.AdminInvestBonusTransactionAPIView.as_view()),
]

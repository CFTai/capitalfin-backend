from django import urls

from api_admin.goldmine import views

urlpatterns = [
    urls.path("settings/", views.AdminGoldmineBonusSettingsAPIView.as_view()),
    urls.path(
        "settings/<int:pk>/", views.AdminGoldmineBonusSettingsDetailsAPIView.as_view()
    ),
    urls.path("bonus/", views.AdminGoldmineBonusTransactionAPIView.as_view()),
    urls.path(
        "bonus/<int:pk>/", views.AdminGoldmineBonusTransactionDetailsAPIView.as_view()
    ),
]

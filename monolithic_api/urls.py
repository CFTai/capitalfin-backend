"""
URL configuration for monolithic_api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from drf_yasg import views as drf_yasg_views, openapi as drf_yasg_openapi

from rest_framework import permissions

from rest_framework_simplejwt import views as jwt_views

schema_view = drf_yasg_views.get_schema_view(
    drf_yasg_openapi.Info(title="APIs", default_version="1.0.0"),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("", schema_view.with_ui("swagger", cache_timeout=0), name="api-schema"),
    path("django/admin/", admin.site.urls),
    path("token/", jwt_views.TokenObtainPairView.as_view(), name="token-obtain-pair"),
    path("token/refresh/", jwt_views.TokenRefreshView.as_view(), name="token-refresh"),
    path("admin/", include("api_admin.urls")),
    path("upload/", include("upload.urls")),
    path("users/", include("user.urls")),
    path("referrals/", include("referral.urls")),
    path("accounts/", include("account.urls")),
    path("banks/", include("bank.urls")),
    path("transactions/", include("transaction.urls")),
    path("blockchain/", include("blockchain.urls")),
    path("withdrawals/", include("withdrawal.urls")),
    path("terms/", include("term.urls")),
    path("stakes/", include("stake.urls")),
    path("contracts/", include("contract.urls")),
    path("invests/", include("invest.urls")),
]

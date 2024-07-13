from django import urls

from user import views

urlpatterns = [
    urls.path("register/", views.RegistrationAPIView.as_view(), name="registration"),
    urls.path("profile/", views.ProfileAPIView.as_view(), name="profile"),
    urls.path("password/", views.PasswordAPIView.as_view(), name="password"),
    urls.path(
        "password/forget/",
        views.ForgetPasswordAPIView.as_view(),
        name="forget password",
    ),
    urls.path(
        "password/reset/", views.ResetPasswordAPIView.as_view(), name="reset password"
    ),
]

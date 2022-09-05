from django.urls import path, include
from django.views.generic import TemplateView
from . import views


urlpatterns = [
    path("login/", views.LoginAPIView.as_view(), name="account_login"),
    path("reset/password/", views.PasswordResetView.as_view(), name="rest_password_reset"),
    path("password/change/",views.ChangePasswordView.as_view(),name="rest_password_change",),
    path("", include("rest_auth.urls")),
    path("sign-up/", views.RegisterAPIView.as_view(), name="signup"),
    path("account-confirm-email/sent/", TemplateView.as_view(),name="account_confirm_email",),
    path("password/reset/confirm/<str:uidb64>/<str:token>/",views.PasswordResetConfirmView.as_view(),name="password_reset_confirm",),
    path("google-login/", views.GoogleSocialAuthView.as_view(), name="google_login"),
]
 
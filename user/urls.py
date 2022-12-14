from django.urls import path, include
from . import views


urlpatterns = [
    path("login/", views.LoginAPIView.as_view(), name="account_login"),
    path("reset/password/", views.PasswordResetView.as_view(), name="rest_password_reset"),
    path("password/change/",views.ChangePasswordView.as_view(),name="rest_password_change",),
    path("", include("rest_auth.urls")),
    path("sign-up/", views.RegisterAPIView.as_view(), name="signup"),
    path("resend-verification-email/",views.ResendEmailVerificationView.as_view(),name="resend_verification_email"),
    path("account-confirm-email/<str:key>",views.VerifyEmailView.as_view(),name="rest_verify_email"),
    path("password/reset/confirm/<str:uidb64>/<str:token>/",views.PasswordResetConfirmView.as_view(),name="password_reset_confirm",),
    path("google-login/", views.GoogleSocialAuthView.as_view(), name="google_login"),
    path("google-signin/", views.GoogleLoginAPIView.as_view(), name="google_signin"),
    path('profile/', views.ProfileAPIView.as_view(), name="profile"),
    path('logout/', views.LogoutView.as_view(), name='logout'),
]
 
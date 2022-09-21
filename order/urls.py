from django.urls import path
from . import views
from . import stripe_webhook

urlpatterns = [
    path('success', views.SuccessView.as_view()),
    path('cancel', views.SuccessView.as_view()),
    path('checkout', views.CreateCheckoutSessionView.as_view(), name="checkout_session"),
    path('stripe-webhook', stripe_webhook.stripe_webhook, name="stripe_webhook"),
]
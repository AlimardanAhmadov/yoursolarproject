from django.urls import path
from . import views

urlpatterns = [
    path('/success', views.SuccessView.as_view()),
    path('/cancel', views.SuccessView.as_view()),
]
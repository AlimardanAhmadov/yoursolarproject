from . import views
from django.urls import path

urlpatterns = [
    path('quote-builder', views.QuoteBuilderView.as_view(), name='quote_builder')
]
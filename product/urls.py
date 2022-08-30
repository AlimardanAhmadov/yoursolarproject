from django.urls import path
from . import views


urlpatterns = [
    path('products/<str:slug>', views.ProductDetailView.as_view(), name='selected_product'),
]
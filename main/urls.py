from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='home'),
    path('e-shop/', views.ProductsAPIView.as_view(), name="shop")
]
from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='home'),
    path('how-to-videos/', views.how_to_videos, name='how_to_videos'),
    path('e-shop/', views.ProductsAPIView.as_view(), name="shop")
]
from django.urls import path
from . import views


urlpatterns = [
    path('add-to-cart/<str:slug>/<str:username>/', views.CreateCartItemView.as_view()),
    path('update-cart/<str:slug>/', views.UpdateCartView.as_view()),
    path('remove-item/<str:slug>/', views.DestroyCartItemAPIView.as_view()),
]
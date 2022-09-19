from . import views
from django.urls import path

urlpatterns = [
    path('build-quote/section', views.QuoteBuilderView.as_view(), name='quote_builder'),
    path('upload-products/', views.UploadProductsView.as_view(), name='upload_products'),
    path('upload-objects/', views.LoadObjectsView.as_view(), name='upload_objects'),
    path('variant-details/<slug:slug>', views.DisplayVariantDetailsView.as_view(), name='variant_details'),
    path('quote/<slug:slug>', views.QuoteView.as_view(), name='quote'),
]
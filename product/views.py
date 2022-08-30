from django.shortcuts import get_object_or_404
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from main.html_renderer import MyHTMLRenderer
from .serializers import ProductSerializer, ProductVariantSerializer
from .models import Product, ProductVariant


class ProductDetailView(APIView):
    permission_classes = (permissions.AllowAny,)
    template_name = 'main/product_details.html'
    renderer_classes = [MyHTMLRenderer,]
    serializer_class = ProductSerializer

    def get(self, request, slug):
        selected_product = Product.cache_by_slug(slug)

        if not selected_product:
            selected_product = get_object_or_404(Product, slug=slug)
        
        product_variants = ProductVariant.objects.filter(selected_product=selected_product)
       
        product_serializer = ProductSerializer(selected_product, context={"request": request})
        variant_serializer = ProductVariantSerializer(product_variants, many=True)
        
        context = {
            'product_variants': variant_serializer.data,
            'product': product_serializer.data,
            'status': status.HTTP_200_OK,
        }
        return Response(context)

   
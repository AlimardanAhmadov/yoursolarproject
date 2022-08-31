from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.http import JsonResponse
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from main.html_renderer import MyHTMLRenderer
from .serializers import ProductSerializer, ProductVariantSerializer
from .models import Product, ProductVariant


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


class ProductDetailView(APIView):
    permission_classes = (permissions.AllowAny,)
    template_name = 'main/product_details.html'
    renderer_classes = [MyHTMLRenderer,]
    serializer_class = ProductSerializer

    def get(self, request, slug, variant=None):
        variant_slug = request.GET.get('variant_slug')
        selected_product = Product.cache_by_slug(slug)

        if not selected_product:
            selected_product = get_object_or_404(Product, slug=slug)
        
        product_variants = ProductVariant.objects.filter(selected_product=selected_product)

        product_serializer = ProductSerializer(selected_product)
        variant_serializer = ProductVariantSerializer(product_variants, many=True)
        
        context = {
            'product_variants': variant_serializer.data,
            'product': product_serializer.data,
            'status': status.HTTP_200_OK,
        }

        if is_ajax(request=request):
            if variant_slug is not None:
                selected_variant = ProductVariant.cache_by_slug(variant_slug)

                if selected_variant is None:
                    try:
                        selected_variant = get_object_or_404(ProductVariant, slug=variant_slug)
                    except ProductVariant.DoesNotExist:
                        selected_variant = None
                
                selected_variant_serializer = ProductVariantSerializer(selected_variant)
                
                html = render_to_string(
                    template_name="main/variant-details.html",
                    context={"selected_variant": selected_variant_serializer.data}
                )
                
                data_dict = {"html_from_view": html}

                return JsonResponse(data=data_dict, safe=False)
        
        return Response(context)

   
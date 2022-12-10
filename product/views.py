import random

from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from main.html_renderer import MyHTMLRenderer
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Product, ProductVariant
from .serializers import ProductSerializer, ProductVariantSerializer


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


class ProductDetailView(APIView):
    permission_classes = (permissions.AllowAny,)
    template_name = 'main/product_details.html'
    renderer_classes = [MyHTMLRenderer,]
    serializer_class = ProductSerializer
    
    def dispatch(self, *args, **kwargs):
        return super(ProductDetailView, self).dispatch(*args, **kwargs)

    def get(self, request, slug, variant=None):
        variant_slug = request.GET.get('variant_slug')
        selected_product = Product.cache_by_slug(slug)

        if not selected_product:
            selected_product = get_object_or_404(Product, slug=slug)
        
        product_variants = ProductVariant.objects.filter(selected_product=selected_product).exclude(availability='Out of stock')

        product_serializer = ProductSerializer(selected_product)
        variant_serializer = ProductVariantSerializer(product_variants, many=True)

        #related products
        products = list(Product.objects.filter(Q(category=selected_product.category)).exclude(slug=slug))

        list_length = len(products)

        if list_length < 4:
            related_products = random.sample(products, list_length)
        else:
            related_products = random.sample(products, 4)
        
        context = {
            'product_variants': variant_serializer.data,
            'related_products': related_products,
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


                if selected_variant.selected_product.category == 'Cables':
                    context={"selected_variant": selected_variant_serializer.data, "sizes": product_variants.values('slug', 'cable_size').distinct()}
                else:
                    context={"selected_variant": selected_variant_serializer.data}
                
                html = render_to_string(
                    template_name="main/variant-details.html",
                    context=context
                )
                
                data_dict = {"html_from_view": html}

                return JsonResponse(data=data_dict, safe=False)
        
        return Response(context)

   
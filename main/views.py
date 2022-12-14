import json
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from product.models import Product
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from main.html_renderer import MyHTMLRenderer


def index(request):
    return render(request, 'main/base.html')

def how_to_videos(request):
    return render(request, 'main/howtovideos.html')

def thescience(request):
    return render(request, 'main/thescience.html')

def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

class ProductsAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    template_name = 'main/products.html'
    renderer_classes = [MyHTMLRenderer, ]
    
    def dispatch(self, *args, **kwargs):
        return super(ProductsAPIView, self).dispatch(*args, **kwargs)

    def get(self, request, q=None, category=None, brand=None):
        page = request.GET.get('page', 1)
        
        q = request.GET.get('q', None)
        categories = request.GET.getlist('category[]')
        brand = request.GET.getlist('brand[]')
        is_ajax = request.GET.get('is_ajax')

        nested_list = [[q,], categories, brand]

        if nested_list[0][0] is None and not any(nested_list[1]):
            matching_items = Product.objects.all()
        elif nested_list[0][0] is None:
            product_lookup = Q(brand__in=brand) & Q(category__in=categories)
            matching_items = Product.objects.filter(product_lookup)
        else:
            product_lookup = Q(title__icontains=q) & Q(brand__in=brand) & Q(category__in=categories)
            matching_items = Product.objects.filter(product_lookup)
        

        if is_ajax == 'True':
            html = render_to_string(
                template_name="main/product-results.html",
                context={"results": matching_items}
            )
            
            data_dict = {"html_from_view": html}
            return JsonResponse(data=data_dict, safe=False)
     
        else:
            paginator = Paginator(matching_items, 20)

            try:
                products = paginator.page(page)
            except PageNotAnInteger:
                products = paginator.page(1)
            except EmptyPage:
                products = paginator.page(paginator.num_pages)

            context = {
                "products": products,
                'has_next': products.has_next(),
                'has_prev': products.has_previous(),
                'status': status.HTTP_200_OK,
            }
            return Response(context)

from django.shortcuts import render
from django.db.models import Q
from django.template.loader import render_to_string
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework import permissions, status
from rest_framework.response import Response

from main.html_renderer import MyHTMLRenderer
from product.models import Product


def index(request):
    return render(request, 'main/base.html')

def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

class ProductsAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    template_name = 'main/products.html'
    renderer_classes = [MyHTMLRenderer, ]
    paginate_by = 2


    def dispatch(self, *args, **kwargs):
        return super(ProductsAPIView, self).dispatch(*args, **kwargs)

    def get(self, request, q=None, category=None, availability=None, brand=None, wattage=None):
        page = request.GET.get('page', 1)
        
        q = request.GET.get('q', None)
        categories = request.GET.getlist('category[]')
        availability = request.GET.getlist('availability[]')
        brand = request.GET.getlist('brand[]')
        wattage = request.GET.getlist('wattage[]')
        is_ajax = request.GET.get('is_ajax')

        nested_list = [[q,], categories, availability, brand, wattage]

        if nested_list[0][0] is None and not any(nested_list[1:4]):
            matching_items = Product.objects.all()
        elif q is None:
            product_lookup = Q(brand__in=brand) & Q(availability__in=availability) & Q(category__in=categories)
            matching_items = Product.objects.filter(product_lookup)
        else:
            product_lookup = Q(title__icontains=q) & Q(brand__in=brand) & Q(availability__in=availability) & Q(category__in=categories)
            matching_items = Product.objects.filter(product_lookup)

        #if is_ajax(request=request):
        if is_ajax == 'True':
            html = render_to_string(
                template_name="main/product-results.html",
                context={"products": matching_items}
            )
            
            data_dict = {"html_from_view": html}

            return JsonResponse(data=data_dict, safe=False)
        else:
            paginator = Paginator(matching_items, 10)

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
                'count': matching_items.count(),
            }
            return Response(context)

import re, json
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from main.views import is_ajax
from product.models import Product, ProductVariant
from product.serializers import ProductVariantSerializer

from rest_framework.generics import (
    ListCreateAPIView,
)
from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response

from django.contrib.auth.decorators import login_required 
from django.utils.decorators import method_decorator
from django.db import transaction

from main.html_renderer import MyHTMLRenderer
from .serializers import QuoteBuilderSerializer



class QuoteBuilderView(ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    template_name = 'quote/quote_builder.html'
    renderer_classes = [MyHTMLRenderer,]
    serializer_class = QuoteBuilderSerializer
    queryset = ""

    @method_decorator(login_required(login_url='/login/'))
    def dispatch(self, *args, **kwargs):
        return super(QuoteBuilderView, self).dispatch(*args, **kwargs)
    
    def get_serializer(self, *args, **kwargs):
        return QuoteBuilderSerializer(*args, **kwargs)
    
    def get(self, request, format=None):
        serializer = QuoteBuilderSerializer(context={'request': request})
        return Response(data=serializer.data)

    def create(self, request, *args, **kwargs):
        with transaction.atomic():
            try:
                serializer = self.get_serializer(data=request.data, context={'request': request})
                if serializer.is_valid():
                    self.perform_create_quote(serializer)
                    return JsonResponse(serializer.data, status=status.HTTP_200_OK)
                else:
                    data = []
                    emessage=serializer.errors
                    for key in emessage:
                        err_message = str(emessage[key])
                        err_string = re.search("string='(.*)', ", err_message)
                        message_value = err_string.group(1)
                        final_message = f"{key} - {message_value}"
                        data.append(final_message)

                    response = HttpResponse(json.dumps({'err': data}), 
                        content_type='application/json')
                    response.status_code = 400
                    return response

            except Exception:
                transaction.set_rollback(True)
                response = HttpResponse(json.dumps({'err': ["Something went wrong!"]}), 
                    content_type='application/json')
                response.status_code = 400
                return response

    def perform_create_quote(self, serializer):
        quote = serializer.save()
        return quote


class UploadProductsView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ProductVariantSerializer

    def get(self, request):
        if is_ajax(request=request):
            page = request.GET.get('page', 1)
            product_type = request.GET.get('product_type')
            variants = ProductVariant.objects.filter(Q(selected_product__category=product_type))
            paginator = Paginator(variants, 10)

            try:
                variants = paginator.page(page)
            except PageNotAnInteger:
                variants = paginator.page(1)
            except EmptyPage:
                variants = paginator.page(paginator.num_pages)
            
            serializer = ProductVariantSerializer(variants, many=True)

            if product_type == 'Panels':
                template_name="quote/quote_pages/choose-solar-panel.html"
            elif product_type == 'Fitting':
                template_name="quote/quote_pages/select-fittings.html"
            elif product_type == 'Inverter':
                template_name="quote/quote_pages/select-inverter.html"

            html = render_to_string(
                template_name=template_name,
                context={"products": serializer.data}
            )
            
            data_dict = {"html_from_view": html}

            return JsonResponse(data=data_dict, safe=False)


class DisplayVariantDetailsView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ProductVariantSerializer

    def get(self, request, slug):
        if is_ajax(request=request):
            variant = ProductVariant.cache_by_slug(slug)

            if variant is None:
                variant = get_object_or_404(ProductVariant, slug=slug)
            
            serializer = ProductVariantSerializer(variant, many=False)

            html = render_to_string(
                template_name="quote/quote_pages/selected-product-modal.html",
                context={"product": serializer.data}
            )
            
            data_dict = {"html_from_view": html}

            return JsonResponse(data=data_dict, safe=False)


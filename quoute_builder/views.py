import json
import re

from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from main.html_renderer import MyHTMLRenderer
from main.views import is_ajax
from product.models import ProductVariant
from product.serializers import ProductVariantSerializer
from rest_framework import permissions, status
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Quote, Service, StorageSystem
from .serializers import (QuoteBuilderSerializer, QuoteSerializer,
                          ServiceSerializer, StorageSystemSerializer)


class QuoteView(APIView):
    permission_classes = (permissions.IsAuthenticated, )
    template_name = 'quote/quote_pages/summary.html'
    renderer_classes = [MyHTMLRenderer, ]
    serializer_class = QuoteSerializer


    @method_decorator(login_required(login_url='/login/'))
    def dispatch(self, *args, **kwargs):
        return super(QuoteView, self).dispatch(*args, **kwargs)

    def get(self, request, slug):
        selected_quote = Quote.cache_by_slug(slug)
        if selected_quote is None:
            selected_quote = get_object_or_404(Quote, slug=slug)

        serializer = QuoteSerializer(selected_quote, many=False)

        context = {
            'data': serializer.data,
            'storages': StorageSystem.objects.all(),
            'status': status.HTTP_200_OK
        }

        return Response(context)


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
                    context = {
                        'data': serializer.data,
                        'status': status.HTTP_200_OK,
                        'redirect_url': serializer.data['slug']
                    }
                    return JsonResponse(context)
                else:
                    data = []
                    emessage=serializer.errors
                    print(emessage)

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
            except Exception as e:
                print(e)


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
            roof_type = request.GET.get('roof_type')
            slug = request.GET.get('slug')

            if product_type == 'Inverter':
                selected_panel = ProductVariant.cache_by_slug(slug)
                if selected_panel is None:
                    selected_panel = get_object_or_404(ProductVariant, slug=slug)
                variants = ProductVariant.objects.filter(Q(selected_product__category__iexact=product_type) & Q(wattage__gte=selected_panel.wattage)).exclude(availability='Out of stock')
            
            elif product_type == 'Fitting':
                if roof_type:
                    variants = ProductVariant.objects.filter(Q(selected_product__category__iexact=product_type) & Q(suitable_roof_style__iexact=roof_type)).exclude(availability='Out of stock')
            else:
                variants = ProductVariant.objects.filter(Q(selected_product__category=product_type)).exclude(availability='Out of stock')
                

            paginator = Paginator(variants, 10)

            try:
                variants = paginator.page(page)
            except PageNotAnInteger:
                variants = paginator.page(1)
            except EmptyPage:
                variants = paginator.page(paginator.num_pages)
            
            serializer = ProductVariantSerializer(variants, many=True)

            if product_type == 'Panel':
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
            
            variant = get_object_or_404(ProductVariant, slug=slug)
            
            serializer = ProductVariantSerializer(variant)

            html = render_to_string(
                template_name="quote/quote_pages/selected-product-modal.html",
                context={"product": serializer.data}
            )
            
            data_dict = {"html_from_view": html}

            return JsonResponse(data=data_dict, safe=False)


class LoadObjectsView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ServiceSerializer

    def get(self, request):
        if is_ajax(request=request):
            object_type = request.GET.get('object_type')

            if object_type == 'storage-system-size':
                storages = StorageSystem.objects.all()
                serializer = StorageSystemSerializer(storages, many=True)
                template_name="quote/quote_pages/storage-system-size.html"
                
            elif object_type == 'extra-help':
                services = Service.objects.all()
                serializer = ServiceSerializer(services, many=True)
                template_name="quote/quote_pages/extra-help.html"

            html = render_to_string(
                template_name=template_name,
                context={"objects": serializer.data}
            )
            
            data_dict = {"html_from_view": html}

            return JsonResponse(data=data_dict, safe=False)


class QuotesAPIView(APIView):
    serializer_class = QuoteSerializer
    permission_class = (permissions.IsAuthenticated, )
    template_name = 'quote/quotes.html'
    renderer_classes = [MyHTMLRenderer, ]

    @method_decorator(login_required(login_url='/login/'))
    def dispatch(self, *args, **kwargs):
        return super(QuotesAPIView, self).dispatch(*args, **kwargs)

    def get_serializer(self, *args, **kwargs):
        return QuoteSerializer(*args, **kwargs)
    
    def get(self, request):
        page = request.GET.get('page', 1)

        current_user = request.user
        
        quotes = Quote.objects.filter(user=current_user)
        self.serializer = self.get_serializer(quotes, many=True)

        paginator = Paginator(quotes, 10)

        try:
            quotes = paginator.page(page)
        except PageNotAnInteger:
            quotes = paginator.page(1)
        except EmptyPage:
            quotes = paginator.page(paginator.num_pages)
        context = {
            'quotes': quotes,
            'status': status.HTTP_200_OK,
        }
        return Response(context)

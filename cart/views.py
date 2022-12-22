import json
import re
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.utils.text import slugify
from main.ajax_decorator import ajax_login_required
from product.models import Product
from quoute_builder.models import Quote
from rest_framework import permissions, status
from rest_framework.generics import ListCreateAPIView

from .models import Cart, CartItem
from .serializers import (CartDetailsItemSerializer, CreateCartItemSerializer,
                          UpdateCartSerializer)


class CreateCartItemView(ListCreateAPIView):
    permission_classes = (permissions.AllowAny,)
    allowed_methods = ("POST", "OPTIONS", "HEAD", "GET")
    serializer_class = CreateCartItemSerializer
    queryset = ""

    @method_decorator(ajax_login_required)
    def dispatch(self, *args, **kwargs):
        return super(CreateCartItemView, self).dispatch(*args, **kwargs)

    def get_product(self, slug, variant=None):
        selected_product = Product.cache_by_slug(slug)

        if not selected_product:
            selected_product = get_object_or_404(Product, slug=slug)
        return selected_product
    
    def get_cart(self, request, variant=None):
        if request.user.is_authenticated:
            username = self.request.user.email.split("@")[0]
            print(username)
            current_cart = Cart.cache_by_slug(slugify(username))

            if not current_cart:
                current_cart = get_object_or_404(Cart, slug=slugify(username))
        else:

            guest = request.session['nonuser']
            current_cart = Cart.cache_by_slug(slugify(guest))

            if not current_cart:
                current_cart = Cart.objects.get(session_id = guest, slug=guest)
        return current_cart


    def create(self, request, slug, variant=None):
        with transaction.atomic():
            try:
                serializer = CreateCartItemSerializer(
                    data=request.data,
                    context={
                        "request": request, 
                        "product": self.get_product(slug), 
                        "variant_slug": request.POST.get('variant_slug'),
                        "cart": self.get_cart(request)
                    }
                )
                if serializer.is_valid():
                    self.perform_create(serializer)
                    context = {
                        'serializer': serializer.data,
                        'status': status.HTTP_200_OK,
                    }

                    return JsonResponse(context)
                else:
                    transaction.set_rollback(True)
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

            except Exception as e:
                print("Error: ", e)
                transaction.set_rollback(True)
                response = HttpResponse(json.dumps({'err': ["Something went wrong!"]}), 
                    content_type='application/json')
                response.status_code = 400
                return response

    def perform_create(self, serializer):
        cart_serializer = serializer.save()
        return cart_serializer


class UpdateCartView(ListCreateAPIView):
    permission_classes = (permissions.AllowAny,)
    allowed_methods = ("POST", "OPTIONS", "HEAD", "GET")
    serializer_class = UpdateCartSerializer
    queryset = ""

    def dispatch(self, *args, **kwargs):
        return super(UpdateCartView, self).dispatch(*args, **kwargs)

    def get_object(self, slug):
        selected_product = get_object_or_404(CartItem, slug=slug)
        return selected_product
    
    def create(self, request, slug):
        with transaction.atomic():
            try:
                serializer = UpdateCartSerializer(
                    data=request.data, 
                    context={
                        "request": request, 
                        "product": self.get_object(slug), 
                    }
                )
                if serializer.is_valid():
                    self.perform_create(serializer)
                    context = {
                        'data': serializer.data,
                        'status': status.HTTP_200_OK,
                    }
                    return JsonResponse(context)
                else:
                    transaction.set_rollback(True)
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
            except Exception as e:
                print(e)
                transaction.set_rollback(True)
                response = HttpResponse(json.dumps({'err': ["Something went wrong!"]}), 
                    content_type='application/json')
                response.status_code = 400
                return response

    def perform_create(self, serializer):
        update_serializer = serializer.save()
        return update_serializer


class DestroyCartItemAPIView(ListCreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = CartDetailsItemSerializer
    queryset = ""
    allowed_methods = ("POST", "OPTIONS", "HEAD")

    def dispatch(self, *args, **kwargs):
        return super(DestroyCartItemAPIView, self).dispatch(*args, **kwargs)

    def get_object(self, slug):
        selected_item = get_object_or_404(CartItem, slug=slug)    
        return selected_item
    
    def create(self, request, slug):
        instance = self.get_object(slug)

        if isinstance(instance.content_object, Quote):
            quote_slug = instance.content_object.slug
            quote = Quote.cache_by_slug(quote_slug)

            if not quote:
                quote = instance.content_object
            
            quote.delete()

        instance.delete()
        
        context = {
            'detail': 'Product delete'
        }

        return JsonResponse(context)

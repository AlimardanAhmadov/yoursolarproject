import json, re
from django.shortcuts import get_object_or_404
from django.utils.text import slugify
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required 
from django.db import transaction
from django.http import JsonResponse, HttpResponse
from rest_framework.generics import ListCreateAPIView
from rest_framework import permissions, status
from rest_framework.response import Response

from .serializers import CartItemSerializer
from .models import Cart
from product.models import Product


class CreateCartItemView(ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    allowed_methods = ("POST", "OPTIONS", "HEAD", "GET")
    serializer_class = CartItemSerializer

    @method_decorator(login_required(login_url='***'))
    def dispatch(self, *args, **kwargs):
        return super(CreateCartItemView, self).dispatch(*args, **kwargs)

    def get_product(self, slug):
        selected_product = Product.cache_by_slug(slug)

        if not selected_product:
            selected_product = get_object_or_404(Product, slug=slug)
        
        return selected_product
    
    def get_cart(self, username):
        current_cart = Cart.cache_by_slug(slugify(username))

        if not current_cart:
            current_cart = get_object_or_404(Cart, slug=slugify(username))
        
        return current_cart

    def get(self, request, slug, username):
        serializer = CartItemSerializer(
            self.get_cart(), 
            data=request.data, 
            context={
                "request": request, 
                "product": self.get_product(), 
                "cart": self.get_cart()
            }
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, slug, username):
        with transaction.atomic():
            try:
                serializer = CartItemSerializer(self.get_cart(), data=request.data, context={"request": request})
                if serializer.is_valid():

                    serializer = CartItemSerializer(
                        self.get_cart(), 
                        data=request.data, 
                        context={
                            "request": request, 
                            "product": self.get_product(), 
                            "cart": self.get_cart()
                        }
                    )
                    self.perform_create(serializer)
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

    def perform_create(self, serializer):
        cart_serializer = serializer.save()
        return cart_serializer
from django.contrib.gis.geoip2 import GeoIP2
from django.utils.text import slugify
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.db.models import Sum

from cart.serializers import CartItemSerializer, CartSerializer
from cart.models import Cart, CartItem


def geoip(request):
    if settings.DEBUG == False:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        
        g = GeoIP2()
        location = g.city(ip)
        location_country = location["country_name"]
        context = {
            "location_country": location_country,
        }

        return context
    else:
        return {}


def cart_items(request):
    if request.user.is_authenticated:
        current_user = request.user

        current_cart = Cart.cache_by_slug(slugify(current_user.username))

        if current_cart is None:
            current_cart = Cart.objects.filter(slug=slugify(current_user.username)).first()

        cart_serializer = CartSerializer(current_cart, many=False)

        context = {
            'cart': cart_serializer.data,
            'qty': CartItem.objects.filter(cart=current_cart).aggregate(Sum('quantity'))['quantity__sum'] or 0
        }

        # cart items 
        items_exists = CartItem.objects.filter(cart=current_cart).exists()

        if items_exists:
            cart_items = CartItem.objects.filter(cart=current_cart)

            cart_item_serializer = CartItemSerializer(cart_items, many=True)
            context['total_cost'] = current_cart.total_cost
            context['items'] = cart_item_serializer.data

        return context
    else:
        return {}
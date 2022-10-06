import json
import uuid
from cart.models import Cart, CartItem
from cart.serializers import CartSerializer
from django.conf import settings
from django.contrib.gis.geoip2 import GeoIP2
from django.db.models import Sum
from django.utils.text import slugify


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
        location_code = location["country_code"].lower()

        context = {
            "location_country": location_country,
            "location_code": location_code,
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

    else:
        try:
            guest = request.session['nonuser']
            current_cart = Cart.cache_by_slug(slugify(guest))

            if not current_cart:
                current_cart = Cart.objects.get(session_id = guest, slug=guest)
        except Exception:
            request.session['nonuser'] = str(uuid.uuid4())
            current_cart = Cart.objects.create(session_id = request.session['nonuser'], slug=request.session['nonuser'])
    
    cart_serializer = CartSerializer(current_cart, many=False)
    
    context = {
        'cart': cart_serializer.data,
        'qty': CartItem.objects.filter(cart=current_cart).aggregate(Sum('quantity'))['quantity__sum'] or 0
    }

    # cart items 
    items_exists = CartItem.objects.filter(cart=current_cart).exists()

    if items_exists:
        cart_items = CartItem.objects.filter(cart=current_cart)

        context['cart_total'] = current_cart.total_cost
        context['cart_items'] = cart_items

    return context

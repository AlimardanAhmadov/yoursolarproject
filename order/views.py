import json, stripe, os
from django.shortcuts import get_object_or_404, redirect
from django.conf import settings
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views import View
from django.conf import settings
from django.utils.decorators import method_decorator


from main.utils import no_generator

from cart.models import Cart, CartItem
from product.models import ProductVariant
from quoute_builder.models import Quote
from .models import Order, OrderItem


stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY')

MY_DOMAIN = os.environ.get("MY_DOMAIN")


class SuccessView(TemplateView):
    template_name = "stripe/success.html"


class CancelView(TemplateView):
    template_name = "stripe/cancel.html"


class CreateCheckoutSessionView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(CreateCheckoutSessionView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        user = request.user

        cart = Cart.cache_by_slug(str(user.username))
        if not cart:
            cart = get_object_or_404(Cart, slug=str(user.username))

        line_items = []
        order_items = CartItem.objects.filter(cart=cart).exists()

        if order_items:
            for item in CartItem.objects.filter(cart=cart):
                
                product = item.content_object

                if isinstance(product, Quote):
                    image = MY_DOMAIN + product.selected_panel.image.url
                elif isinstance(product, ProductVariant):
                    image = MY_DOMAIN + product.image.url
                else:
                    image = "https://i.imgur.com/EHyR2nP.png"
                            
                line_items.append(
                    {
                        'price_data': {
                            'currency': 'usd',
                            'unit_amount': int(item.grand_total) * 100,
                            'product_data': {
                                'name': product.title,
                                'images': [image],
                            },
                        },
                        'quantity': item.quantity,
                    }
                )

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card', 'afterpay_clearpay'],
            line_items=line_items,
            metadata={"order_id": no_generator(),'user_email': request.user.email,},
            mode='payment',
            success_url=MY_DOMAIN + '/success',
            cancel_url=MY_DOMAIN + '/cancel',
            billing_address_collection="required",
            shipping_address_collection={
                'allowed_countries': ['GB',],
            },
        )
        return redirect(checkout_session.url, code=303)

 
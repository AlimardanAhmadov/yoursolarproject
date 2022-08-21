import json, stripe, os
from tabnanny import check
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.views import View
from django.db.models import Sum

from main.utils import no_generator

from cart.models import Cart, CartItem
from .models import Order, OrderItem


stripe.api_key = settings.STRIPE_SECRET_KEY

MY_DOMAIN = os.environ.get("MY_DOMAIN")


class SuccessView(TemplateView):
    template_name = "success.html"


class CancelView(TemplateView):
    template_name = "cancel.html"


class CreateCheckoutSessionView(View):
    def post(self, request, *args, **kwargs):
        cart_slug = self.kwargs["slug"]
        cart = Cart.cache_by_slug(cart_slug)
        if not cart:
            cart = get_object_or_404(Cart, slug=cart_slug)

        line_items = []
        order_items = CartItem.objects.filter(cart=cart).exists()

        new_order = Order.objects.create(
            user=request.user,
            order_number=checkout_session.metadata['order_id'],
            is_paid=True,
            total=cart.grand_total
        )

        if order_items:
            for item in CartItem.objects.filter(cart=cart):
                OrderItem.objects.create(
                    order=new_order,
                    product=item,
                    quantity=item.quantity,
                    total=item.price
                )
                
                product = item.model_type.get_object_for_this_type(slug=item.slug)

                line_items.append(
                    {
                        'price_data': {
                            'currency': 'usd',
                            'unit_amount': item.total,
                            'product_data': {
                                'name': product.title,
                                'images': ['https://i.imgur.com/EHyR2nP.png'],
                            },
                        },
                        'quantity': item.quantity,
                    }
                )

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            metadata={"order_id": no_generator()},
            mode='payment',
            success_url=MY_DOMAIN + '/success',
            cancel_url=MY_DOMAIN + '/cancel',
        )
        return JsonResponse({
            'id': checkout_session.id
        })


class StripeIntentView(View):
    def post(self, request, *args, **kwargs):
        try:
            req_json = json.loads(request.body)
            customer = stripe.Customer.create(email=req_json['email'])
            cart_slug = self.kwargs["slug"]

            cart = Cart.cache_by_slug(cart_slug)
            if not cart:
                cart = get_object_or_404(Cart, slug=cart_slug)

            intent = stripe.PaymentIntent.create(
                amount=cart.grand_total,
                currency='usd',
                customer=customer['id'],
                metadata={
                    "order_id": no_generator()
                }
            )
            return JsonResponse({
                'clientSecret': intent['client_secret']
            })
        except Exception as e:
            return JsonResponse({ 'error': str(e) })

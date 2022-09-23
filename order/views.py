import json, stripe, os
from locale import currency
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.conf import settings
from django.utils.decorators import method_decorator

from main.utils import no_generator

from cart.models import Cart, CartItem
from product.models import ProductVariant
from quoute_builder.models import Quote


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
        try:
            user = request.user

            cart = Cart.cache_by_slug(str(user.username))
            if not cart:
                cart = get_object_or_404(Cart, slug=str(user.username))
            
            line_items = []
            order_items = CartItem.objects.filter(cart=cart).exists()

            # create tax id
            tax_id = stripe.TaxRate.create(
                display_name="VAT",
                description="VAT UK",
                jurisdiction="UK",
                percentage=20,
                inclusive=False,
            )

            # createa customer for successful/failed notification
            try:
                stripe.Customer.retrieve(request.user.email)
            except Exception:
                stripe.Customer.create(
                    description=request.user.username,
                    email=request.user.email,
                )


            if order_items:
                for item in CartItem.objects.filter(cart=cart):
                    
                    product = item.content_object

                    if item.quantity > product.quantity:
                        if product.quantity < 1:
                            message = '{} is out of stock!'.format(product.title)
                            response = HttpResponse(json.dumps({'err': message}), 
                                content_type='application/json')
                            response.status_code = 400
                            return response
                        else:
                            message = 'You cannot order more than {} of {}'.format(product.quantity, product.title)
                            response = HttpResponse(json.dumps({'err': message}), 
                                content_type='application/json')
                            response.status_code = 400
                            return response

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
                                'unit_amount': int(item.price) * 100,
                                'product_data': {
                                    'name': product.title,
                                    'images': [image],
                                },
                            },
                            'quantity': item.quantity,
                            'tax_rates': [tax_id['id']]
                        }
                    )

            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card', 'afterpay_clearpay'],
                line_items=line_items,
                metadata={"order_id": no_generator(),'user_email': request.user.email, 'user_username': request.user.username},
                customer_email=request.user.email,
                mode='payment',
                success_url=MY_DOMAIN + '/success',
                cancel_url=MY_DOMAIN + '/cancel',
                billing_address_collection="required",
                shipping_address_collection={
                    'allowed_countries': ['GB',],
                },
            )
            
            return JsonResponse({
                'checkout_session_url': checkout_session.url,
                'code': 303
            })
        except Exception as exc:
            print(exc)
            response = HttpResponse(json.dumps({'err': "Something went wrong! Please try again."}), 
                content_type='application/json')
            response.status_code = 400
            return response


class SingleProductCreateCheckoutSessionView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(SingleProductCreateCheckoutSessionView, self).dispatch(*args, **kwargs)

    def post(self, request, slug, *args, **kwargs):
        try:
            try:
                selected_product = Quote.cache_by_slug(slug)

                if not selected_product:
                    selected_product = Quote.objects.get(slug=slug)
                
                if selected_product.paid:

                    response = HttpResponse(json.dumps({'err': "You can't order this quote more than once"}), 
                        content_type='application/json')
                    response.status_code = 400
                    return response

                elif selected_product.selected_panel.quantity < selected_product.panels_count:

                    if selected_product.selected_panel.quantity < 1:
                        message = '{} is out of stock! Please contact us.'.format(selected_product.selected_panel.title)
                        response = HttpResponse(json.dumps({'err': message}), 
                            content_type='application/json')
                        response.status_code = 400
                        return response

                    else:
                        message = 'You cannot order more than {} of {}. Please contact us.'.format(selected_product.selected_panel.quantity, selected_product.selected_panel.title)
                        response = HttpResponse(json.dumps({'err': message}), 
                            content_type='application/json')
                        response.status_code = 400
                        return response

                elif selected_product.inverter.quantity < 1:
                    message = '{} is out of stock! Please contact us.'.format(selected_product.inverter.title)
                    response = HttpResponse(json.dumps({'err': message}), 
                        content_type='application/json')
                    response.status_code = 400
                    return response

                elif selected_product.fitting.quantity < 1:
                    message = '{} is out of stock! Please contact us.'.format(selected_product.fitting.title)
                    response = HttpResponse(json.dumps({'err': message}), 
                        content_type='application/json')
                    response.status_code = 400
                    return response

                image = MY_DOMAIN + selected_product.selected_panel.image.url
                price = selected_product.total_cost
                title = selected_product.title
                shipping_price = 0.0
                product_id = order_id = selected_product.slug
                max_qty = 1

            except Quote.DoesNotExist:
                selected_product = ProductVariant.cache_by_slug(slug)
                
                if not selected_product:
                    selected_product = ProductVariant.objects.get(slug=slug)

                image = MY_DOMAIN + selected_product.image.url
                price = selected_product.price
                shipping_price = selected_product.shipping_price
                title = selected_product.title
                max_qty = selected_product.quantity
                order_id = no_generator()
                product_id = selected_product.slug
            
            # createa customer for successful/failed notification
            try:
                stripe.Customer.retrieve(request.user.email)
            except Exception:
                stripe.Customer.create(
                    description=request.user.username,
                    email=request.user.email,
                )

            # create tax id
            tax_id = stripe.TaxRate.create(
                display_name="VAT",
                description="VAT UK",
                jurisdiction="UK",
                percentage=20,
                inclusive=False,
            )
            
            line_items = [
                {
                    'price_data': {
                        'currency': 'usd',
                        'unit_amount': int(sum([price,shipping_price])) * 100,
                        'product_data': {
                            'name': title,
                            'images': [image,],
                        },
                    },
                    'adjustable_quantity': {
                        'enabled': True,
                        'minimum': 1,
                        'maximum': int(max_qty),
                    },
                    'quantity': 1,
                    'tax_rates': [tax_id['id']]
                }
            ]

            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card', 'afterpay_clearpay'],
                line_items=line_items,
                metadata={"order_id": order_id,'user_email': request.user.email, 'product_id': product_id},
                mode='payment',
                customer_email=request.user.email,
                success_url=MY_DOMAIN + '/success',
                cancel_url=MY_DOMAIN + '/cancel',
                billing_address_collection="required",
                shipping_address_collection={
                    'allowed_countries': ['GB',],
                },
            )

            return JsonResponse({
                'checkout_session_url': checkout_session.url,
                'code': 303
            })
        except Exception as exc:
            print(exc)
            response = HttpResponse(json.dumps({'err': "Something went wrong! Please try again."}), 
                content_type='application/json')
            response.status_code = 400
            return response
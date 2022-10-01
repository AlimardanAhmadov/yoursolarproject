import json, stripe, os
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.conf import settings
from django.utils.decorators import method_decorator
from main.ajax_decorator import ajax_login_required

from main.utils import no_generator

from cart.models import Cart, CartItem
from product.models import ProductVariant
from quoute_builder.models import Quote
from user.views import get_prev_url


stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY')

MY_DOMAIN = os.environ.get("MY_DOMAIN")


class SuccessView(TemplateView):
    template_name = "stripe/success.html"


class CancelView(TemplateView):
    template_name = "stripe/cancel.html"


class CreateCheckoutSessionView(View):
    @method_decorator([csrf_exempt, ajax_login_required])
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

            # create customer for successful/failed notification
            try:
                stripe.Customer.retrieve(request.user.email)
            except Exception:
                stripe.Customer.create(
                    description=request.user.username,
                    email=request.user.email,
                )
            
            total_shipping = 0

            if order_items:
                for item in CartItem.objects.filter(cart=cart):
                    
                    product = item.content_object
                    if isinstance(product, ProductVariant):
                        product_qty = product.quantity
                        item_price = item.price
                    else:
                        product_qty = 1
                        item_price = item.content_object.total_cost

                    if item.quantity > product_qty:
                        if product_qty < 1:
                            message = '{} is out of stock!'.format(product.title)
                            response = HttpResponse(json.dumps({'err': message}), 
                                content_type='application/json')
                            response.status_code = 400
                            return response
                        else:
                            message = 'You cannot order more than {} of {}'.format(product_qty, product.title)
                            response = HttpResponse(json.dumps({'err': message}), 
                                content_type='application/json')
                            response.status_code = 400
                            return response

                    if isinstance(product, Quote):
                        image = product.selected_panel.image.url
                        product_id = product.slug
                        total_shipping = 0
                    elif isinstance(product, ProductVariant):
                        image = product.image.url
                        product_id = product.slug
                        total_shipping += product.shipping_price
                    else:
                        image = "https://i.imgur.com/EHyR2nP.png"
                                
                    line_items.append(
                        {
                            'price_data': {
                                'currency': 'usd',
                                'unit_amount': int(item_price) * 100,
                                'product_data': {
                                    'name': product.title,
                                    'images': [image, ],
                                },
                            },
                            'quantity': item.quantity,
                            'tax_rates': [tax_id['id']]
                        }
                    )

            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card', 'afterpay_clearpay'],
                line_items=line_items,
                metadata={"order_id": no_generator(),'user_email': request.user.email, 'user_username': request.user.username, 'ordered_product_id': product_id},
                customer_email=request.user.email,
                mode='payment',
                success_url=MY_DOMAIN + "/success?session_id={CHECKOUT_SESSION_ID}",
                cancel_url=get_prev_url(request),
                billing_address_collection="required",
                shipping_address_collection={
                    'allowed_countries': ['GB',],
                },
                shipping_options=[
                    {
                        'shipping_rate_data': {
                            'type': 'fixed_amount',
                            'fixed_amount': {
                            'amount': int(total_shipping) * 100,
                            'currency': 'usd',
                            },
                            'display_name': 'Shipping price',
                        }
                    },
                ],
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
    @method_decorator([csrf_exempt, ajax_login_required])
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

                image = selected_product.selected_panel.image.url
                price = selected_product.total_cost
                title = selected_product.title
                shipping_price = 0.0
                product_id = order_id = selected_product.slug
                max_qty = 1

            except Quote.DoesNotExist:
                selected_product = ProductVariant.cache_by_slug(slug)
                
                if not selected_product:
                    selected_product = ProductVariant.objects.get(slug=slug)

                image = selected_product.image.url
                if selected_product.discount:
                    price = selected_product.discount
                else:
                    price = selected_product.price
                shipping_price = selected_product.shipping_price
                title = selected_product.title
                max_qty = selected_product.quantity
                order_id = no_generator()
                product_id = selected_product.slug
            
            # create customer for successful/failed notification
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
                        'unit_amount': int(price) * 100,
                        'product_data': {
                            'name': title,
                            'images': [image,],
                        },
                    },
                    'adjustable_quantity': {
                        'enabled': True,
                        'maximum': int(max_qty),
                    },
                    'quantity': 1,
                    'tax_rates': [tax_id['id']]
                }
            ]

            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card', 'afterpay_clearpay'],
                line_items=line_items,
                metadata={"order_id": order_id,'user_email': request.user.email, 'product_id': product_id, 'ordered_product_id': product_id},
                mode='payment',
                customer_email=request.user.email,
                success_url=MY_DOMAIN + "/success?session_id={CHECKOUT_SESSION_ID}",
                cancel_url=get_prev_url(request),
                billing_address_collection="required",
                shipping_address_collection={
                    'allowed_countries': ['GB',],
                },
                shipping_options=[
                    {
                        'shipping_rate_data': {
                            'type': 'fixed_amount',
                            'fixed_amount': {
                            'amount': int(shipping_price) * 100,
                            'currency': 'usd',
                            },
                            'display_name': 'Shipping price',
                        }
                    },
                ],
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
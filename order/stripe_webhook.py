from dataclasses import dataclass
import stripe
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType

from cart.models import Cart, CartItem
from order.tasks import confirm_payment_email

from product.models import ProductVariant
from quoute_builder.models import Quote

from .models import Order, OrderItem

User = get_user_model()


stripe_webhook_token = settings.STRIPE_WEBHOOK_SECRET

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, str(stripe_webhook_token)
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']

        order_id = session["metadata"]["order_id"]
        user_email = session["metadata"]["user_email"]

        user = get_object_or_404(User, email=user_email)

        address_key = session['shipping_details']['address']

        address = address_key['line1'] + ',' + address_key['city'] + ',' + address_key['country'] + ',' + address_key['postal_code']

        if address_key['line2']:
            secondary_address = address_key['line2'] + ',' + address_key['city'] + ',' + address_key['country'] + ',' + address_key['postal_code']
        else:
            secondary_address = ""

        new_order = Order.objects.create(
            user=user,
            order_number=order_id,
            total=float(session['amount_total']),
            address = address,
            secondary_address = secondary_address
        )
        items_dct = stripe.checkout.Session.list_line_items(session['id'], limit=500)

        for item in range(0, len(items_dct['data'])):
            amount_total = items_dct.data[item]['amount_total']
            
            OrderItem.objects.create(
                order=new_order,
                total=amount_total/100,
                product_title=items_dct.data[item]['description'],
                product_quantity=items_dct.data[item]['quantity'],
                
            )
        
        # update single product quantity
        if len(items_dct['data']) == 1 and "product_id" in session['metadata']:
            if ProductVariant.objects.filter(slug=session['metadata']['product_id']).exists():
                product = ProductVariant.cache_by_slug(session['metadata']['product_id'])
                if not product:
                    product = get_object_or_404(ProductVariant, slug=session['metadata']['product_id'])
                
                product.quantity -= items_dct['data'][0]['quantity']
                product.save()

            else:
                quote = Quote.cache_by_slug(session['metadata']['product_id'])
                if not quote:
                    quote = get_object_or_404(Quote, slug=session['metadata']['product_id'])
                
                quote.selected_panel.quantity -= quote.panels_count
                quote.selected_panel.save()

                quote.inverter.quantity -= 1
                quote.inverter.save()

                quote.fitting.quantity -= 1
                quote.fitting.save()
                quote.paid=True
                quote.save()

                if CartItem.objects.filter(model_type=ContentType.objects.get_for_model(Quote), object_id=quote.id).exists():
                    CartItem.objects.filter(model_type=ContentType.objects.get_for_model(Quote), object_id=quote.id).first().delete()

        else:
            if "user_username" in session["metadata"]:
                user_username = session["metadata"]["user_username"]

                cart = Cart.cache_by_slug(user_username)
                if not cart:
                    cart = get_object_or_404(Cart, slug=user_username)

                if CartItem.objects.filter(cart=cart).exists():

                    for item in CartItem.objects.filter(cart=cart):
                        if isinstance(item.content_object, Quote):
                            quote = item.content_object
                            quote.selected_panel.quantity -= quote.panels_count
                            quote.selected_panel.save()

                            quote.inverter.quantity -= 1
                            quote.inverter.save()

                            quote.fitting.quantity -= 1
                            quote.fitting.save()
                            quote.paid=True
                            quote.save()
                        else:
                            product = item.content_object
                            product.quantity -= item.quantity
                            product.save()

    else:
        print('Unhandled event type {}'.format(event['type']))

    return HttpResponse(status=200)

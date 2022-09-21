import email
from django.shortcuts import get_object_or_404
import stripe
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.contrib.auth import get_user_model

from .models import Order, OrderItem
from .tasks import confirm_payment_email

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
    except ValueError as e:
        print(e)
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        print(e)
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']

        order_id = session["metadata"]["order_id"]
        user_email = session["metadata"]["user_email"]

        user = get_object_or_404(User, email=user_email)

        new_order = Order.objects.create(
            user=user,
            order_number=order_id,
            is_paid=True,
            total=float(session['amount_total'])
        )
        items_dct = stripe.checkout.Session.list_line_items(session['id'], limit=500)

        for item in range(0, len(items_dct['data'])):
            amount_total = items_dct.data[item]['amount_total']
            OrderItem.objects.create(
                order=new_order,
                total=amount_total/100,
            )

        # confirm_payment_email.delay(order_id)

    else:
        print('Unhandled event type {}'.format(event['type']))

    return HttpResponse(status=200)

from celery import shared_task
from .models import Order

import ssl
ssl._create_default_https_context = ssl._create_unverified_context


url = "http://localhost:8000/"


@shared_task(bind=True, max_retries=20)
def confirm_payment_email(self, order_id):
    order = Order.objects.filter(order_number=order_id).first()
    try:
        order.confirmation()
        return "Email Is Sent"
    except Exception as e:
        print("Email not sent ", e)
        raise self.retry(exc=e, countdown=25200)
    
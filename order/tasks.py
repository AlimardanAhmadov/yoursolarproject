from celery import shared_task
from main.utils import send_email
from . import models

import ssl
ssl._create_default_https_context = ssl._create_unverified_context



@shared_task(bind=True, max_retries=20)
def confirm_payment_email(self, context_dict, subject, recipients, template_name):
    try:
        send_email(context_dict, subject, recipients, template_name, "html")
        return "Email Is Sent"
    except Exception as e:
        print("Email not sent ", e)
        raise self.retry(exc=e, countdown=25200)


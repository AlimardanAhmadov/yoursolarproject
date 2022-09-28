from celery import shared_task

from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes

from main.utils import send_email

from django.contrib.auth import get_user_model

import ssl
ssl._create_default_https_context = ssl._create_unverified_context

User = get_user_model()

url = "http://localhost:8000/"


@shared_task(bind=True, max_retries=20)
def send_register_mail(self, user_id, key):
    user = User.objects.filter(id=user_id).first()

    body = {
        'username': user.username,
        'key': url + 'account-confirm-email/' + key
    }

    subject = "Verify Email Address"
    recipients = [user.email]

    template_name = 'email/activate.html'
    
    try:
        send_email(body, subject, recipients, template_name, "html")
        return "Email Is Sent"
    except Exception as e:
        print("Email not sent ", e)
        raise self.retry(exc=e, countdown=25200)
    
@shared_task(bind=True, max_retries=1)
def send_reset_password_email(self, user_id):
    user = User.objects.get(id=user_id)
    body = {
        'url': url + 'password/reset/confirm/' + urlsafe_base64_encode(force_bytes(user.pk)) + '/' + default_token_generator.make_token(user)
    }
    subject = "Reset Your password"
    recipients = [user.email]

    template_name = 'email/reset_password.html'

    try:
        send_email(body, subject, recipients, template_name, "html")
        return "Email Is Sent"
    except Exception as e:
        print("Email not sent ", e)
        raise self.retry(exc=e, countdown=25200)


from celery import shared_task
from main.utils import send_email
from .models import Quote


url = "https://sopanel.herokuapp.com/"


@shared_task(bind=True, max_retries=20)
def send_confirmation_mail(self, user, quote_id):
    quote = Quote.objects.filter(id=quote_id).first()
    try:
        quote.confirmation()
        return "Email Is Sent"
    except Exception as e:
        print("Email is not sent ", e)
        raise self.retry(exc=e, countdown=25200)
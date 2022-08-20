import logging
from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.utils.text import slugify
from django.conf import settings

from cart.models import CartItem
from main.utils import id_generator, send_email
from main.models import TimeStampedModel

User = get_user_model()

class Order(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_number = models.CharField(max_length=250, blank=True, null=True, unique=True)
    is_paid = models.BooleanField(default=False)
    total = models.FloatField()
    slug = models.SlugField(blank=True, null=True)


    def confirmation(self):

        logging.debug("Sending order summary to %s" % (self.email))

        if all(
            [   
                getattr(settings, 'SENDGRID_API_KEY'),
                getattr(settings, 'EMAIL_HOST'),
                getattr(settings, 'EMAIL_HOST_USER'),
                getattr(settings, 'EMAIL_HOST_PASSWORD'),
                getattr(settings, 'EMAIL_PORT'),
                getattr(settings, 'EMAIL_USE_TLS'),
            ]
        ):
            if self.is_paid:
                body = """<p>
                Hello from Solar Panels!<br><br>
                Order Summary: %s
                Thank you from Solar Panels! <br><br>
                <p>""" % (
                    self.order_number,
                )

                subject = "Order Summary"
                template_name = 'email/order.html'
            
            recipients = [self.email]

            send_email(body, subject, recipients, template_name, "html")
        else:
            logging.warning("Sendgrid credentials are not set")

    @staticmethod
    def post_save(sender, **kwargs):
        instance = kwargs.get('instance')
        created = kwargs.get('created')
        if created:
            instance.slug = slugify(instance.order_number + "-" + str(id_generator()) + "-" + str(instance.pk))
            instance.save()

post_save.connect(Order.post_save, sender=Order)


class OrderItem(TimeStampedModel):
    order = models.ForeignKey(
        Order, related_name="order_items", on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        CartItem, related_name="product_order", on_delete=models.CASCADE
    )
    quantity = models.IntegerField()
    total = models.DecimalField(max_digits=10, decimal_places=2)



import logging
from django.conf import settings
from django.db import models
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save

from main.utils import send_email, id_generator

from phonenumber_field.serializerfields import PhoneNumberField
from product.models import Product

User = get_user_model()

YES_NO_CHOICE = (
    ("Yes", "Yes"),
    ("No", "No"),
)

RAIL_LENGTH =  (
    ("2.2", "2.2"),
    ("3.3", "3.3"),
)


class Quote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    slug = models.SlugField()
    selected_panel = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='panel')
    inverter = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='selected_inverter')
    selected_rail = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='selected_rail')
    title = models.CharField(max_length=250)
    full_name = models.CharField(max_length=150)
    address = models.TextField()
    postcode = models.IntegerField()
    email = models.EmailField(max_length=250)
    phone = models.CharField(max_length=50)
    property_type = models.CharField(max_length=50)
    no_floors = models.IntegerField()
    no_bedrooms = models.IntegerField()
    bill_rate = models.CharField(max_length=10, blank=True, null=True)
    roof_style = models.CharField(max_length=20, blank=True, null=True)
    roof_width = models.FloatField(default=0.0)
    roof_height = models.FloatField(default=0.0)
    panels_count = models.IntegerField(blank=True, null=True)
    fitting = models.CharField(max_length=50, blank=True, null=True)
    rails_count = models.IntegerField(blank=True, null=True)
    cable_length = models.FloatField(blank=True, null=True)
    storage_system_size = models.CharField(max_length=5, blank=True, null=True)
    extra_requirement = models.CharField(max_length=50, blank=True, null=True)
    total_cost = models.FloatField(default=0.0)
    shipping_price = models.FloatField(default=0.0)
    tax = models.FloatField(default=0.0)

    class Meta:
        verbose_name = 'Quote'
        verbose_name_plural = 'Quotes'
        indexes = [models.Index(fields=['user', 'selected_panel', 'id'])]

    def __str__(self):
        return "%s" % self.selected_panel.title

    
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
            if self.completed:
                body = """<p>
                Hello from Solar Panels!<br><br>
                Confirmation Mail: %s
                Thank you from Solar Panels! <br><br>
                <p>""" % (
                    self.product.title,
                )

                subject = "Order Summary"
                template_name = 'email/summary.html'
            else:
                body = """<p>
                Hello from Solar Panels!<br><br>
                Complete your order: %s
                Thank you from Solar Panels! <br><br>
                <p>""" % (
                    self.product.title,
                )

                subject = "Complete your order"
                template_name = 'email/order_warning.html'

            recipients = [self.email]

            send_email(body, subject, recipients, template_name, "html")
        else:
            logging.warning("Sendgrid credentials are not set")


    @staticmethod
    def post_save(sender, **kwargs):
        instance = kwargs.get('instance')
        created = kwargs.get('created')
        if created:
            instance.slug = slugify(str(id_generator()) + "-" + str(instance.id))
            instance.save()

post_save.connect(Quote.post_save, sender=Quote)
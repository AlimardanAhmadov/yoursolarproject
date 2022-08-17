import logging
from django.conf import settings
from django.db import models
from django.contrib.auth import get_user_model

from main.utils import send_email

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

INSTALLATION = (
    ("Roof", "Roof"),
    ("Standalone", "Standalone"),
)

class Quote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    selected_product = models.ForeignKey(Product, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=150)
    address = models.TextField()
    postcode = models.IntegerField()
    email = models.EmailField(max_length=250)
    phone = PhoneNumberField()
    property_type = models.CharField(max_length=50)
    no_floors = models.IntegerField()
    no_bedrooms = models.IntegerField()
    other = models.TextField(blank=True, null=True)
    bill_rate = models.CharField(max_length=10, blank=True, null=True)
    agreement = models.BooleanField(default=False)
    installation_type = models.CharField(max_length=150, choices=INSTALLATION)
    standalone_installation = models.CharField(max_length=70, blank=True, null=True)
    single_phase = models.BooleanField(default=False)
    spare_way = models.BooleanField(default=False)
    roof_style = models.CharField(max_length=20, blank=True, null=True)
    b_no_panels = models.CharField(max_length=4, blank=True, null=True, choices=YES_NO_CHOICE) # yes or no
    width = models.IntegerField(blank=True, null=True)
    height = models.IntegerField(blank=True, null=True)
    # selected_panel_id = models.CharField(max_legth=200)
    panels_count = models.IntegerField(blank=True, null=True)
    fitting = models.CharField(max_length=50, blank=True, null=True)
    mount_style_no = models.CharField(max_length=200, blank=True, null=True)
    rails_count = models.IntegerField(blank=True, null=True)
    rails_length = models.FloatField(blank=True, null=True, choices=RAIL_LENGTH) #2.2M or 3.3M
    cable_length = models.FloatField(blank=True, null=True)
    storage_system_size = models.CharField(max_length=5, blank=True, null=True)
    storage_cost_option = models.CharField(max_length=5, blank=True, null=True)
    help_with = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        verbose_name = 'Quote'
        verbose_name_plural = 'Quotes'
        indexes = [models.Index(fields=['user', 'selected_product', 'id'])]

    def __str__(self):
        return "%s" % self.product.title

    
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

            body = """<p>
            Hello from Solar Panels!<br><br>
            Confirmation Mail: %s
            Thank you from Solar Panels! <br><br>
            <p>""" % (
                self.product.title,
            )

            subject = "Order Summary"
            recipients = [self.email]

            template_name = 'email/summary.html'

            send_email(body, subject, recipients, template_name, "html")
        else:
            logging.warning("Sendgrid credentials are not set")

from email.policy import default
import logging
from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.utils.text import slugify
from django.conf import settings

from datetime import date

from main.utils import id_generator, send_email
from main.models import TimeStampedModel
from order.tasks import confirm_payment_email

User = get_user_model()

class Order(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_number = models.CharField(max_length=250, blank=True, null=True, unique=True)
    status = models.CharField(max_length=250, blank=True, null=True)
    total = models.FloatField()
    slug = models.SlugField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    secondary_address = models.TextField(blank=True, null=True)


    @staticmethod
    def post_save(sender, **kwargs):
        instance = kwargs.get('instance')
        created = kwargs.get('created')
        if created:
            instance.slug = slugify(instance.order_number + "-" + str(id_generator()) + "-" + str(instance.pk))
            instance.save()


post_save.connect(Order.post_save, sender=Order)


class OrderItem(TimeStampedModel):
    order = models.ForeignKey(Order, related_name="order_items", on_delete=models.CASCADE)
    total = models.FloatField(default=0.0)
    product_cover = models.ImageField(default='default.png')
    product_title = models.CharField(max_length=250, blank=True, null=True)
    product_quantity = models.PositiveIntegerField(default=0)
    
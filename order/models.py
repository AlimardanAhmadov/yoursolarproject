from datetime import datetime

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save
from django.utils.text import slugify
from main.models import TimeStampedModel
from main.utils import id_generator

User = get_user_model()

class Order(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_number = models.CharField(max_length=250, blank=True, null=True, unique=True)
    status = models.CharField(max_length=250, blank=True, null=True)
    total = models.FloatField()
    slug = models.SlugField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    secondary_address = models.TextField(blank=True, null=True)
    created = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-id']

    @staticmethod
    def post_save(sender, **kwargs):
        instance = kwargs.get('instance')
        created = kwargs.get('created')
        if created:
            createDate = datetime.now()
            formatedDate = createDate.strftime("%Y-%m-%d %H:%M:%S")
            instance.slug = slugify(instance.order_number + "-" + str(id_generator()) + "-" + str(instance.pk))
            instance.created = formatedDate
            instance.save()


post_save.connect(Order.post_save, sender=Order)


class OrderItem(TimeStampedModel):
    order = models.ForeignKey(Order, related_name="order_items", on_delete=models.CASCADE)
    total = models.FloatField(default=0.0)
    product_title = models.CharField(max_length=250, blank=True, null=True)
    product_quantity = models.PositiveIntegerField(default=0)
    order_product_id = models.CharField("Product ID", max_length=500)

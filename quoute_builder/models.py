import logging
from datetime import datetime

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db import models
from django.db.models.signals import post_delete, post_save
from django.utils.text import slugify
from main.utils import id_generator
from order.tasks import confirm_payment_email
from product.models import ProductVariant

User = get_user_model()


CACHED_SERVICE_BY_SLUG_KEY = 'service__by_slug__{}'
CACHED_STORAGE_BY_SLUG_KEY = 'storage__by_slug__{}'
CACHED_QUOTE_BY_SLUG_KEY = 'quote__by_slug__{}'
CACHE_LENGTH = 24 * 3600  # --> 24hrs

class NotFound:
    """ caching """


class Quote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=250, blank=True, null=True)
    slug = models.SlugField()
    full_name = models.CharField(max_length=150, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    postcode = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(max_length=250, blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    property_type = models.CharField(max_length=50)
    no_floors = models.IntegerField("Number of floors")
    no_bedrooms = models.IntegerField("Number of bedrooms")
    selected_panel = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name='panel', blank=True, null=True)
    panel_price = models.FloatField(default=0.0)
    inverter = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name='selected_inverter', blank=True, null=True)
    inverter_price = models.FloatField(default=0.0)
    rail_type = models.CharField(max_length=5, blank=True, null=True)
    rail_length = models.CharField(max_length=100, blank=True, null=True)
    no_rails = models.CharField("Quantity of rails", max_length=100, blank=True, null=True)
    rail_price = models.CharField("Total rail cost", max_length=100, blank=True, null=True)
    bill_rate = models.CharField(max_length=100, blank=True, null=True)
    roof_style = models.CharField(max_length=20, blank=True, null=True)
    roof_width = models.FloatField(default=0.0)
    roof_height = models.FloatField(default=0.0)
    panels_count = models.IntegerField(blank=True, null=True)
    fitting = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name='selected_fitting', blank=True, null=True)
    fitting_price = models.FloatField(default=0.0)
    cable_length_bat_inv = models.FloatField("Cable Length from battery location to the inverter", blank=True, null=True)
    cable_length_panel_cons = models.FloatField("Cable length from panels to the consumer unit via the Inverter", blank=True, null=True)
    storage_cable = models.FloatField(blank=True, null=True)
    storage_system = models.ForeignKey("StorageSystem", on_delete=models.CASCADE, blank=True, null=True)
    extra_service = models.ForeignKey("Service", on_delete=models.CASCADE, blank=True, null=True)
    shipping_price = models.FloatField(default=200.0)
    equipment_cost = models.FloatField(default=0.0)
    total_cost = models.FloatField(default=0.0)
    tax = models.FloatField(default=20)
    paid = models.BooleanField(default=False)
    created = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = 'Quote'
        verbose_name_plural = 'Quotes'
        indexes = [models.Index(fields=['user', 'selected_panel', 'id'])]
    
    @staticmethod
    def cache_by_slug(slug):
        key = CACHED_QUOTE_BY_SLUG_KEY.format(slug)

        quote = cache.get(key)
        if quote:
            if isinstance(quote, NotFound):
                return None
            return quote

        quote = Quote.objects.filter(slug=slug).first()

        if not quote:
            cache.set(key, NotFound(), CACHE_LENGTH)
            return None

        cache.set(key, quote, CACHE_LENGTH)
        return quote

    @staticmethod
    def invalidate_cache(sender, instance, **kwargs):
        """
        Invalidate the cached data when it is updated or deleted
        """
        cache.delete(CACHED_QUOTE_BY_SLUG_KEY.format(instance.slug))


    def confirmation(self):
        
        logging.debug("Sending quote details to %s" % (self.email))

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
            context_dict = {
                'url': 'https://sopanel.herokuapp.com/quote/' + self.slug
            }
            
            subject = "New Quote"
            template_name = 'email/order.html'
            
            recipients = [self.user.email]

            confirm_payment_email(context_dict, subject, recipients, template_name)

    @staticmethod
    def post_save(sender, **kwargs):
        instance = kwargs.get('instance')
        created = kwargs.get('created')
        if created:
            createDate = datetime.now()
            formatedDate = createDate.strftime("%Y-%m-%d %H:%M:%S")

            instance.slug = slugify(str(id_generator()) + "-" + str(instance.id))
            instance.title = slugify(str(id_generator()) + "-" + str(instance.id))
            instance.created = formatedDate
            instance.save()

            instance.confirmation()

post_save.connect(Quote.post_save, sender=Quote)
post_save.connect(Quote.invalidate_cache, sender=Quote)
post_delete.connect(Quote.invalidate_cache, sender=Quote)


class Service(models.Model):
    service_title = models.CharField(max_length=250)
    service_price = models.CharField(max_length=50, help_text="Please make sure to add £ GBP")

    @staticmethod
    def cache_by_slug(pk):
        key = CACHED_SERVICE_BY_SLUG_KEY.format(pk)

        service = cache.get(key)
        if service:
            if isinstance(service, NotFound):
                return None
            return service

        service = Service.objects.filter(pk=pk).first()

        if not service:
            cache.set(key, NotFound(), CACHE_LENGTH)
            return None

        cache.set(key, service, CACHE_LENGTH)
        return service

    @staticmethod
    def invalidate_cache(sender, instance, **kwargs):
        """
        Invalidate the cached data when it is updated or deleted
        """
        cache.delete(CACHED_SERVICE_BY_SLUG_KEY.format(instance.pk))

post_save.connect(Service.invalidate_cache, sender=Service)
post_delete.connect(Service.invalidate_cache, sender=Service)


class StorageSystem(models.Model):
    storage_size = models.CharField(max_length=250)
    storage_price = models.FloatField(default=0.0)

    @staticmethod
    def cache_by_slug(pk):
        key = CACHED_STORAGE_BY_SLUG_KEY.format(pk)

        storage = cache.get(key)
        if storage:
            if isinstance(storage, NotFound):
                return None
            return storage

        storage = StorageSystem.objects.filter(pk=pk).first()

        if not storage:
            cache.set(key, NotFound(), CACHE_LENGTH)
            return None

        cache.set(key, storage, CACHE_LENGTH)
        return storage

    @staticmethod
    def invalidate_cache(sender, instance, **kwargs):
        """
        Invalidate the cached data when it is updated or deleted
        """
        cache.delete(CACHED_STORAGE_BY_SLUG_KEY.format(instance.pk))

post_save.connect(StorageSystem.invalidate_cache, sender=StorageSystem)
post_delete.connect(StorageSystem.invalidate_cache, sender=StorageSystem)

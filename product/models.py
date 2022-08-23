import base64
from django.db import models
from django.utils.text import slugify
from django.db.models.signals import post_save, post_delete
from django.core.cache import cache
from django.dispatch import receiver
from django.core.files.base import ContentFile

from djrichtextfield.models import RichTextField
from djmoney.models.fields import MoneyField
from model_utils import FieldTracker

from main.compress_img import compress_image
from main.models import TimeStampedModel
from main.utils import id_generator

CACHED_PRODUCT_BY_SLUG_KEY = 'product__by_slug__{}'
CACHED_VARIANT_BY_SLUG_KEY = 'variant__by_slug__{}'
CACHED_INVERTER_BY_SLUG_KEY = 'inverter__by_slug__{}'
CACHE_LENGTH = 24 * 3600  # --> aq 24hrs demekdi


class NotFound:
    """ caching """


def image_directory_path(instance, filename):
    return "photos/{0}/{1}".format(instance.selected_product.title, filename)

def inverters_img_directory_path(instance, filename):
    return "photos/inverters/{0}".format(filename)

class Product(TimeStampedModel):
    slug=models.SlugField(blank=True, null=True)
    title=models.CharField(max_length=250)
    category=models.CharField(max_length=50)
    description=RichTextField()
    return_policy=models.TextField(blank=True, default='This product has no return policy')
    shipping_policy=models.TextField(blank=True, default='This product has no shipping policy')
    availability=models.BooleanField(default=True)
    product_type=models.CharField(max_length=50)
    brand=models.CharField(max_length=100)

    class Meta:
        verbose_name = 'Solar Panel'
        verbose_name_plural = 'Solar Panels'
        indexes = [models.Index(fields=['title', 'slug', 'id', 'brand', 'category'])]
    
    def __str__(self):
        return "%s" % self.title
    
    @staticmethod
    def cache_by_slug(slug):
        key = CACHED_PRODUCT_BY_SLUG_KEY.format(slug)

        product = cache.get(key)
        if product:
            if isinstance(product, NotFound):
                return None
            return product

        product = Product.objects.filter(slug=slug).first()

        if not product:
            cache.set(key, NotFound(), CACHE_LENGTH)
            return None

        cache.set(key, product, CACHE_LENGTH)
        return product

    @staticmethod
    def post_save(sender, **kwargs):
        instance = kwargs.get('instance')
        created = kwargs.get('created')
        if created:
            instance.slug = slugify(instance.title + "-" + str(id_generator()) + "-" + str(instance.pk))
            instance.save()

post_save.connect(Product.post_save, sender=Product)


@receiver((post_delete, post_save), sender=Product)
def invalidate_coach_cache(sender, instance, **kwargs):
    """
    Invalidate the product cached data when it is updated or deleted
    """
    cache.delete(CACHED_PRODUCT_BY_SLUG_KEY.format(instance.slug))



class ProductVariant(TimeStampedModel):
    selected_product=models.ForeignKey(Product, on_delete=models.CASCADE)
    slug=models.SlugField(blank=True, null=True)
    primary_variant=models.BooleanField(default=False)
    dimensions=models.CharField(max_length=50)
    materials=models.CharField(max_length=100)
    price=MoneyField(max_digits=14, decimal_places=2, default_currency='USD')
    discount=MoneyField(max_digits=14, decimal_places=2, default_currency='USD')
    image=models.ImageField(upload_to=image_directory_path, default='default.png')
    image_url=models.URLField(blank=True, null=True)
    sku=models.CharField(max_length=400)
    active=models.BooleanField(default=True)
    quantity=models.PositiveIntegerField(default=0)
    shipping_price=models.FloatField(default=0.0)
    tax=models.FloatField(default=0.0)

    tracker = FieldTracker()

    class Meta:
        verbose_name = 'Variant'
        verbose_name_plural = 'Variants'
        indexes = [models.Index(fields=['selected_product', 'slug', 'id', 'active',])]

    def save(self, *args, **kwargs):
        url_changed = self.tracker.has_changed('image_url')
        if url_changed:
            image = self.image
            if image and image.size > (0.3 * 1024 * 1024):
                self.image = compress_image(image)

            if ';base64,' in self.image_url:
                format, imgstr = self.image_url.split(';base64,')
                ext = format.split('/')[-1]
                data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
                self.image = data
        super(ProductVariant, self).save(*args, **kwargs)

    @staticmethod
    def cache_by_slug(slug):
        key = CACHED_PRODUCT_BY_SLUG_KEY.format(slug)

        variant = cache.get(key)
        if variant:
            if isinstance(variant, NotFound):
                return None
            return variant

        variant = ProductVariant.objects.filter(slug=slug).first()

        if not variant:
            cache.set(key, NotFound(), CACHE_LENGTH)
            return None

        cache.set(key, variant, CACHE_LENGTH)
        return variant

    @staticmethod
    def post_save(sender, **kwargs):
        instance = kwargs.get('instance')
        created = kwargs.get('created')
        if created:
            instance.slug = slugify(str(id_generator()) + "-" + str(instance.id))
            instance.save()

post_save.connect(ProductVariant.post_save, sender=ProductVariant)


@receiver((post_delete, post_save), sender=ProductVariant)
def invalidate_coach_cache(sender, instance, **kwargs):
    """
    Invalidate the variant cached data when it is updated or deleted
    """
    cache.delete(CACHED_VARIANT_BY_SLUG_KEY.format(instance.slug))


class Inverter(TimeStampedModel):
    slug=models.SlugField(blank=True, null=True)
    cost = models.FloatField()
    title = models.CharField(max_length=200)
    img = models.ImageField(upload_to=inverters_img_directory_path, default='default.png')
    image_url=models.URLField(blank=True, null=True)
    wattage_capacity = models.FloatField()

    class Meta:
        verbose_name = 'Inverter'
        verbose_name_plural = 'Inverters'
        indexes = [models.Index(fields=['wattage_capacity', 'id', ])]

    
    def save(self, *args, **kwargs):
        url_changed = self.tracker.has_changed('image_url')
        if url_changed:
            image = self.img
            if image and image.size > (0.3 * 1024 * 1024):
                self.image = compress_image(image)

            if ';base64,' in self.image_url:
                format, imgstr = self.image_url.split(';base64,')
                ext = format.split('/')[-1]
                data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
                self.img = data
        super(Inverter, self).save(*args, **kwargs)

    @staticmethod
    def post_save(sender, **kwargs):
        instance = kwargs.get('instance')
        created = kwargs.get('created')
        if created:
            instance.slug = slugify(str(id_generator()) + "-" + str(instance.id))
            instance.save()

    @staticmethod
    def cache_by_slug(slug):
        key = CACHED_INVERTER_BY_SLUG_KEY.format(slug)

        inverter = cache.get(key)
        if inverter:
            if isinstance(inverter, NotFound):
                return None
            return inverter

        inverter = Inverter.objects.filter(slug=slug).first()

        if not inverter:
            cache.set(key, NotFound(), CACHE_LENGTH)
            return None

        cache.set(key, inverter, CACHE_LENGTH)
        return inverter

post_save.connect(Inverter.post_save, sender=Inverter)

@receiver((post_delete, post_save), sender=Inverter)
def invalidate_coach_cache(sender, instance, **kwargs):
    """
    Invalidate the inverter cached data when it is updated or deleted
    """
    cache.delete(CACHED_INVERTER_BY_SLUG_KEY.format(instance.slug))
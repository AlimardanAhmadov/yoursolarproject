import random, string
from django.db import models
from django.utils.text import slugify
from django.db.models.signals import post_save, post_delete
from django.core.cache import cache
from django.dispatch import receiver

from djrichtextfield.models import RichTextField
from djmoney.models.fields import MoneyField

from main.models import TimeStampedModel


CACHED_PRODUCT_BY_SLUG_KEY = 'product__by_slug__{}'
CACHED_VARIANT_BY_SLUG_KEY = 'variant__by_slug__{}'
CACHE_LENGTH = 24 * 3600  # --> aq 24hrs demekdi


class NotFound:
    """ caching """

def id_generator(size=8, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def image_directory_path(instance, filename):
    return "photos/{0}/{1}".format(instance.selected_product.title, filename)

class Product(TimeStampedModel):
    slug=models.SlugField()
    title=models.CharField(max_length=250)
    category=models.CharField(max_length=50)
    description=RichTextField()
    tax=models.FloatField(default=0.0)
    return_policy=models.TextField(blank=True, default='This product has no return policy')
    shipping_policy=models.TextField(blank=True, default='This product has no shipping policy')
    availability=models.BooleanField(default=True)
    product_type=models.CharField(max_length=50)
    brand=models.CharField(max_length=100)


    class Meta:
        verbose_name = 'Solar Panel'
        verbose_name_plural = 'Solar Panels'
        indexes = [models.Index(fields=['title', 'slug', 'id', 'brand', 'category'])]
    
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
            instance.slug = slugify(instance.title + "-" + id_generator() + "-" + instance.id)
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
    slug=models.SlugField()
    primary_variant=models.BooleanField(default=False)
    dimensions=models.CharField(max_length=50)
    materials=models.CharField(max_length=100)
    price=MoneyField(max_digits=14, decimal_places=2, default_currency='USD')
    discount=MoneyField(max_digits=14, decimal_places=2, default_currency='USD')
    image=models.ImageField(upload_to=image_directory_path, default='default.png')
    sku=models.CharField(max_length=400)
    active=models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Variant'
        verbose_name_plural = 'Variants'
        indexes = [models.Index(fields=['selected_product', 'slug', 'id', 'active',])]
    
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
            instance.slug = slugify(id_generator() + "-" + instance.id)
            instance.save()

post_save.connect(ProductVariant.post_save, sender=ProductVariant)

@receiver((post_delete, post_save), sender=Product)
def invalidate_coach_cache(sender, instance, **kwargs):
    """
    Invalidate the variant cached data when it is updated or deleted
    """
    cache.delete(CACHED_VARIANT_BY_SLUG_KEY.format(instance.slug))

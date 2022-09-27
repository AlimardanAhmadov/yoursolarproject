from django.db import models
from django.utils.text import slugify
from django.db.models.signals import post_save, post_delete
from django.core.cache import cache

from djrichtextfield.models import RichTextField
from model_utils import FieldTracker

from main.compress_img import compress_image
from main.models import TimeStampedModel
from main.utils import id_generator

CACHED_PRODUCT_BY_SLUG_KEY = 'product__by_slug__{}'
CACHED_VARIANT_BY_SLUG_KEY = 'variant__by_slug__{}'
CACHE_LENGTH = 24 * 3600  # --> 24hrs

class NotFound:
    """ caching """


def image_directory_path(instance, filename):
    return "photos/{0}/{1}".format(instance.selected_product.title, filename)

AV_CHOICES = (
    ('In Stock', 'In stock'),
    ('Out of stock', 'Out of stock'),
)

CATEGORY_CHOICES = (
    ('Inverter', 'Inverter'),
    ('Panel', 'Panel'),
    ('Rail', 'Rail'),
    ('Fitting', 'Fitting'),
    ('Battery', 'Battery'),
    ('Clip', 'Clip'),
    ('Other', 'Other'),
)


ROOF_TYPES = (
    ('Flat Roof', 'Flat Roof'),
    ('Pantile Roof', 'Pantile Roof'),
    ('Flat tile or slate', 'Flat tile or slate'),
    ('Meta Roof', 'Metal Roof'),
    ('New build', 'New build'),
)

class Product(TimeStampedModel):
    slug=models.SlugField(blank=True, null=True, max_length=500)
    title=models.CharField(max_length=250)
    category=models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    return_policy=models.TextField(blank=True, default='This product has no return policy')
    shipping_policy=models.TextField(blank=True, default='This product has no shipping policy')
    brand=models.CharField(max_length=100)
    primary_price=models.FloatField(default=0.0)
    primary_discount=models.FloatField(default=0.0)
    primary_image_url=models.TextField(blank=True, null=True)
    special_offer=models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        indexes = [models.Index(fields=['title', 'slug', 'id', 'brand', 'category'])]
        ordering = ['-id']
    
    
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

    def invalidate_coach_cache(sender, instance, **kwargs):
        """
        Invalidate the product cached data when it is updated or deleted
        """
        cache.delete(CACHED_PRODUCT_BY_SLUG_KEY.format(instance.slug))

    @staticmethod
    def post_save(sender, **kwargs):
        instance = kwargs.get('instance')
        created = kwargs.get('created')
        if created:
            instance.slug = slugify(instance.title + "-" + str(id_generator()) + "-" + str(instance.pk))
            instance.save()

post_save.connect(Product.post_save, sender=Product)
post_save.connect(Product.invalidate_coach_cache, sender=Product)
post_delete.connect(Product.invalidate_coach_cache, sender=Product)


class ProductVariant(TimeStampedModel):
    selected_product=models.ForeignKey(Product, on_delete=models.CASCADE, related_name='related_product')
    title=models.CharField(max_length=200, blank=True, null=True)
    slug=models.SlugField(blank=True, null=True)
    primary_variant=models.BooleanField(default=False)
    description=RichTextField()
    availability=models.CharField(max_length=15, choices=AV_CHOICES)
    width = models.CharField(max_length=50, blank=True, null=True, help_text="For panels. (metres)")
    height = models.CharField(max_length=50, blank=True, null=True, help_text="For panels. (metres)")
    materials=models.TextField(blank=True, null=True)
    price=models.FloatField(default=0.0)
    discount=models.FloatField(default=0.0)
    image=models.ImageField(upload_to=image_directory_path, default='default.png')
    sku=models.CharField(max_length=400)
    active=models.BooleanField(default=True)
    quantity=models.PositiveIntegerField(default=0)
    shipping_price=models.FloatField(default=0.0)
    size = models.CharField(max_length=10, blank=True, null=True, help_text='For cables')
    suitable_roof_style = models.CharField(max_length=20, blank=True, null=True, choices=ROOF_TYPES, help_text='For Hooks/Fittings')
    wattage = models.CharField(max_length=10, blank=True, null=True)
    tracker = FieldTracker()

    class Meta:
        verbose_name = 'Variant'
        verbose_name_plural = 'Variants'
        indexes = [models.Index(fields=['selected_product', 'slug', 'id', 'active',])]
    

    def __str__(self):
        return "Product ID: {} -- Title: {}".format(self.slug, self.title)
    
    def save(self, *args, **kwargs):
        image_changed = self.tracker.has_changed('image')
        quantity = self.tracker.has_changed('quantity')
        primary_variant_changed = self.tracker.has_changed('primary_variant')

        image = self.image

        if quantity:
            if self.quantity <= 0:
                self.availability = 'Out of stock'

        if image_changed:
            if primary_variant_changed and self.primary_variant is True:
                self.selected_product.primary_image_url = self.image.url
                self.selected_product.save()

        if image and image.size > (0.3 * 1024 * 1024):
            self.image = compress_image(image)
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
    def invalidate_coach_cache(sender, instance, **kwargs):
        """
        Invalidate the variant cached data when it is updated or deleted
        """
        print("deleting cache")
        cache.delete(CACHED_VARIANT_BY_SLUG_KEY.format(instance.slug))

    @staticmethod
    def post_save(sender, **kwargs):
        instance = kwargs.get('instance')
        created = kwargs.get('created')

        image_changed = instance.tracker.has_changed('image')

        if image_changed:
            if instance.primary_variant is True:

                instance.selected_product.primary_image_url = instance.image.url
                instance.selected_product.save()
        if created:
            instance.slug = slugify(str(id_generator()) + "-" + str(instance.id))
            instance.save()

post_save.connect(ProductVariant.post_save, sender=ProductVariant)
post_save.connect(ProductVariant.invalidate_coach_cache, sender=ProductVariant)
post_delete.connect(ProductVariant.invalidate_coach_cache, sender=ProductVariant)

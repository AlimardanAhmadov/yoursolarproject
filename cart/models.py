from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db.models.signals import post_save, post_delete
from django.utils.text import slugify
from django.core.cache import cache
from django.contrib.contenttypes.models import ContentType
from django.dispatch import receiver
from django.db.models import Sum
from main.utils import id_generator
from model_utils import FieldTracker
from product.models import ProductVariant


User = get_user_model()

CACHED_CART_BY_SLUG_KEY = 'cart__by_slug__{}'
CACHE_LENGTH = 24 * 3600  # --> 24hrs


class NotFound:
    """ caching """

class Cart(models.Model):
    user = models.OneToOneField(User, related_name='cart', on_delete=models.CASCADE)
    total_cost = models.FloatField(default=0.0)
    grand_total = models.FloatField(default=0.0)
    shipping_cost = models.FloatField(default=0.0)
    slug = models.SlugField(blank=True, null=True)

    def __str__(self):
        return self.user.username
    
    @staticmethod
    def cache_by_slug(slug):
        key = CACHED_CART_BY_SLUG_KEY.format(slug)

        cart = cache.get(key)
        if cart:
            if isinstance(cart, NotFound):
                return None
            return cart

        cart = Cart.objects.filter(slug=slug).first()

        if not cart:
            cache.set(key, NotFound(), CACHE_LENGTH)
            return None

        cache.set(key, cart, CACHE_LENGTH)
        return cart

    @staticmethod
    def invalidate_coach_cache(sender, instance, **kwargs):
        """
        Invalidate the cart cached data when it is updated or deleted
        """
        cache.delete(CACHED_CART_BY_SLUG_KEY.format(instance.slug))

post_save.connect(Cart.invalidate_coach_cache, sender=Cart)
post_delete.connect(Cart.invalidate_coach_cache, sender=Cart)


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    model_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.FloatField(default=0.0)
    total_cost = models.FloatField(default=0.0)
    grand_total = models.FloatField(default=0.0)
    product_id = models.CharField(max_length=250)
    variant_id = models.CharField(max_length=250)
    slug = models.SlugField(blank=True, null=True)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('model_type', 'object_id')

    tracker = FieldTracker()

    class Meta:
        indexes = [
            models.Index(fields=["model_type", "object_id", "cart"]),
        ]

    def save(self, *args, **kwargs):
        quantity = self.tracker.has_changed('quantity')
        
        if quantity:
            if isinstance(self.content_object, ProductVariant):
                total_cost = float(self.price) * int(self.quantity)
                grand_total = total_cost + float(self.content_object.shipping_price)
            else:
                total_cost = float(self.content_object.total_cost) * int(self.quantity)
                grand_total = total_cost

            self.total_cost = total_cost
            self.grand_total = grand_total
        super(CartItem, self).save(*args, **kwargs)

    @staticmethod
    def post_save(sender, *args, **kwargs):
        instance = kwargs.get('instance')
        created = kwargs.get('created')

        if isinstance(instance.content_object, ProductVariant):
            total_cost = float(instance.price) * int(instance.quantity)
            grand_total = total_cost + float(instance.content_object.shipping_price)
        else:
            total_cost = float(instance.content_object.total_cost) * int(instance.quantity)
            grand_total = total_cost

        if created:
            instance.slug = slugify(str(id_generator()) + "-" + str(instance.pk))
            instance.total_cost = total_cost
            instance.grand_total = grand_total
            instance.save()
        
        quantity = instance.tracker.has_changed('quantity')
        if quantity:
            instance.cart.grand_total = CartItem.objects.filter(cart=instance.cart).aggregate(Sum('grand_total'))['grand_total__sum']
            instance.cart.total_cost = CartItem.objects.filter(cart=instance.cart).aggregate(Sum('total_cost'))['total_cost__sum']
            instance.cart.save()

post_save.connect(CartItem.post_save, sender=CartItem)


@receiver(post_delete, sender=CartItem)
def update_cart_on_delete(sender, instance, **kwargs):
    if CartItem.objects.filter(cart=instance.cart).exists():
        instance.cart.grand_total = CartItem.objects.filter(cart=instance.cart).aggregate(Sum('grand_total'))['grand_total__sum']
        instance.cart.total_cost = CartItem.objects.filter(cart=instance.cart).aggregate(Sum('total_cost'))['total_cost__sum']
        instance.cart.save()

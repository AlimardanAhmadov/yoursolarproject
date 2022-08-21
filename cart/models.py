from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db.models.signals import post_save, post_delete
from django.utils.text import slugify
from django.core.cache import cache
from django.contrib.contenttypes.models import ContentType
from django.dispatch import receiver
from main.utils import id_generator
from product.models import Product


User = get_user_model()

CACHED_CART_BY_USERNAME_KEY = 'cart__by_username__{}'
CACHE_LENGTH = 24 * 3600  # --> aq 24hrs demekdi


class NotFound:
    """ caching """

class Cart(models.Model):
    user = models.OneToOneField(User, related_name='cart', on_delete=models.CASCADE)
    total_cost = models.DecimalField(max_digits=5, decimal_places=4)
    grand_total = models.DecimalField(max_digits=5, decimal_places=4, blank=True, null=True)
    tax = models.DecimalField(max_digits=5, decimal_places=4, blank=True, null=True)
    shipping_cost = models.DecimalField(max_digits=5, decimal_places=4, blank=True, null=True)
    qty = models.PositiveIntegerField(blank=True, null=True)
    products = models.ManyToManyField("CartItem", related_name='products', blank=True)
    slug = models.SlugField(blank=True, null=True)

    def __str__(self):
        return self.user.username

    @staticmethod
    def cache_by_slug(slug):
        key = CACHED_CART_BY_USERNAME_KEY.format(slug)

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
    def post_save(sender, **kwargs):
        instance = kwargs.get('instance')
        created = kwargs.get('created')
        if created:
            instance.slug = slugify(instance.user.username)
            instance.save()

post_save.connect(Cart.post_save, sender=Cart)

@receiver((post_delete, post_save), sender=Product)
def invalidate_coach_cache(sender, instance, **kwargs):
    """
    Invalidate the cart cached data when it is updated or deleted
    """
    cache.delete(CACHED_CART_BY_USERNAME_KEY.format(instance.slug))



class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    model_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=6, decimal_places=5)
    product_id = models.CharField(max_length=250)
    slug = models.SlugField(blank=True, null=True)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('model_type', 'object_id')


    class Meta:
        indexes = [
            models.Index(fields=["model_type", "object_id"]),
        ]

    @staticmethod
    def post_save(sender, *args, **kwargs):
        instance = kwargs.get('instance')
        created = kwargs.get('created')
        if created:
            instance.slug = slugify(str(id_generator()) + "-" + str(instance.pk))
            instance.save()

post_save.connect(CartItem.post_save, sender=CartItem)

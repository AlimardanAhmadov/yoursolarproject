from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, post_delete
from django.core.cache import cache
from django.contrib.contenttypes.models import ContentType
from django.dispatch import receiver
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

    def __str__(self):
        return self.user.username

    @staticmethod
    def cache_by_slug(username):
        key = CACHED_CART_BY_USERNAME_KEY.format(username)

        cart = cache.get(key)
        if cart:
            if isinstance(cart, NotFound):
                return None
            return cart

        cart = Cart.objects.filter(username=username).first()

        if not cart:
            cache.set(key, NotFound(), CACHE_LENGTH)
            return None

        cache.set(key, cart, CACHE_LENGTH)
        return cart


@receiver((post_delete, post_save), sender=Product)
def invalidate_coach_cache(sender, instance, **kwargs):
    """
    Invalidate the product cached data when it is updated or deleted
    """
    cache.delete(CACHED_CART_BY_USERNAME_KEY.format(instance.slug))



class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    model_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=6, decimal_places=5)
    product_id = models.CharField(max_length=250)
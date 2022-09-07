from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Cart


User = get_user_model()


@receiver(post_save, sender=User)
def create_user_cart(sender, created, *args, **kwargs):
    instance = kwargs.get('instance')
    if created:
        try:
            if instance.provider == 'Email':
                Cart.objects.create(user=instance, slug=slugify(instance.username))
        except:
            print("Coudn't create a cart")
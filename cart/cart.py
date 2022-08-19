from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Cart


User = get_user_model()


@receiver(post_save, sender=User)
def create_user_cart(sender, created, instance, *args, **kwargs):
    if created:
        try:
            Cart.objects.create(user=instance)
        except:
            print("Coudn't create a cart")
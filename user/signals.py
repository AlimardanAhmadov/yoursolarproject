from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from allauth.account.models import EmailAddress
from user.models import Business, Customer

User = get_user_model()


@receiver(post_save, sender=EmailAddress)
def activate_google_users(sender, created, *args, **kwargs):
    instance = kwargs.get('instance')
    if created:
        try:
            if Customer.objects.filter(user=instance.user).exists():
                profile = Customer.objects.filter(user=instance.user).first()
            elif Business.objects.filter(user=instance.user).exists():
                profile = Business.objects.filter(user=instance.user).first()

            if profile.provider == 'Google':
                instance.verified = True
                instance.save()
        except Exception as exc:
            print("Err: ", exc)
from django.db.models.signals import post_save
from django.dispatch import receiver

from allauth.account.models import EmailAddress


@receiver(post_save, sender=EmailAddress)
def activate_google_users(sender, created, *args, **kwargs):
    instance = kwargs.get('instance')
    if created:
        try:
            if instance.user.customer.provider == 'Google' or instance.user.business.provider == 'Google':
                instance.verified = True
                instance.save()
        except Exception as exc:
            print("Err: ", exc)
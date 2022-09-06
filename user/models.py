from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.utils.text import slugify
from phonenumber_field.modelfields import PhoneNumberField
from djrichtextfield.models import RichTextField

from main.models import TimeStampedModel
from main.utils import id_generator

User = get_user_model()


USER_TYPES = (
    ("Individual", "Individual"),
    ("Bussiness", "Bussiness"),
)

PROVIDER_TYPES = (
    ("Google", "Google"),
    ("Email", "Email"),
)

class Customer(TimeStampedModel):
    user=models.OneToOneField(User, related_name='customer', on_delete=models.CASCADE)
    slug=models.SlugField(blank=True, null=True)
    full_name=models.CharField(max_length=250)
    provider=models.CharField(max_length=10, choices=PROVIDER_TYPES)
    
    class Meta:
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'
        indexes = [models.Index(fields=['user', 'slug',])]
    
    def __str__(self):
        return "%s" % self.user.username


    @staticmethod
    def post_save(sender, **kwargs):
        instance = kwargs.get('instance')
        created = kwargs.get('created')
        if created:
            instance.slug = slugify(str(id_generator()) + "-" + instance.user.username)
            instance.save()

post_save.connect(Customer.post_save, sender=Customer)


class Business(TimeStampedModel):
    user=models.OneToOneField(User, related_name='business', on_delete=models.CASCADE)
    slug=models.SlugField(blank=True, null=True)
    company_name=models.CharField(max_length=250, unique=True, blank=True, null=True)
    provider=models.CharField(max_length=10, choices=PROVIDER_TYPES)
    
    class Meta:
        verbose_name = 'Business'
        verbose_name_plural = 'Businesses'
        indexes = [models.Index(fields=['user', 'slug',])]
    
    def __str__(self):
        return "%s" % self.user.username


    @staticmethod
    def post_save(sender, **kwargs):
        instance = kwargs.get('instance')
        created = kwargs.get('created')
        if created:
            instance.slug = slugify(str(id_generator()) + "-" + instance.user.username)
            instance.save()

post_save.connect(Business.post_save, sender=Business)


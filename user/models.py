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
    account_type=models.CharField(max_length=10, choices=USER_TYPES)
    slug=models.SlugField()
    full_name=models.CharField(max_length=250)
    address=models.TextField()
    postcode=models.PositiveIntegerField()
    property_type=models.CharField(max_length=50)
    no_floors=models.PositiveSmallIntegerField()
    no_bedrooms=models.PositiveSmallIntegerField()
    bill_rate=models.PositiveIntegerField()
    agreement=models.BooleanField(default=False)
    company_name=models.CharField(max_length=250, unique=True, blank=True, null=True)
    other=RichTextField(blank=True)
    phone=PhoneNumberField()
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
            instance.slug = slugify(id_generator() + "-" + instance.user.username)
            instance.save()

post_save.connect(Customer.post_save, sender=Customer)


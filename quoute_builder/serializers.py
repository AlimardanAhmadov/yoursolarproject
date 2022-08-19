import logging
from django.contrib.contenttypes.models import ContentType
from cart.models import CartItem
from phonenumber_field.serializerfields import PhoneNumberField
from product.models import Inverter, Product
from .models import Quote
from rest_framework import serializers



class QuoteBuilderSerializer(serializers.Serializer):    
    selected_panel = serializers.CharField(required=True)
    inverter = serializers.CharField(required=True)
    full_name = serializers.CharField(required=True)
    address = serializers.CharField(required=True)
    postcode = serializers.IntegerField(required=True)
    email = serializers.EmailField(required=True)
    property_type = serializers.CharField(required=True)
    no_floors = serializers.IntegerField(required=True)
    no_bedrooms = serializers.IntegerField(required=True)
    phone = PhoneNumberField()
    other = serializers.CharField(required=False)
    bill_rate = serializers.CharField(required=False)
    agreement = serializers.BooleanField(default=False)
    installation_type = serializers.CharField(required=True) # on a roof or standalone
    standalone_installation = serializers.CharField(required=False)
    spare_way = serializers.BooleanField(default=False)
    roof_style = serializers.CharField(required=False)
    b_no_panels = serializers.CharField(required=False) # yes or no
    width = serializers.FloatField(required=False, default=0.0)
    height = serializers.FloatField(required=False, default=0.0)
    panels_count = serializers.IntegerField(required=False, default=0)
    fitting = serializers.CharField(required=False)
    mount_style_no = serializers.CharField(required=False)
    rails_count = serializers.IntegerField(required=False, default=0)
    rails_length = serializers.FloatField(required=False, default=0.0) #2.2M or 3.3M
    cable_length = serializers.FloatField(required=False, default=0.0)
    storage_system_size = serializers.CharField(required=False)
    storage_cost_option = serializers.CharField(required=False)
    help_with = serializers.CharField(required=False)
    completed = serializers.BooleanField(default=True)
    total_cost = serializers.FloatField(default=0.0)
    quantity = serializers.IntegerField(default=0)
    

    def __init__(self, *args, **kwargs):
        super(QuoteBuilderSerializer, self).__init__(*args, **kwargs)
        self.request = self.context.get("request")
        self.user = getattr(self.request, "user", None)
        self.cart = self.user.cart

    
    def get_cleaned_data(self):
        return {
            "full_name": self.validated_data.get("full_name", ""),
            "address": self.validated_data.get("address", ""),
            "postcode": self.validated_data.get("postcode", ""),
            "email": self.validated_data.get("email", ""),
            "property_type": self.validated_data.get("property_type", ""),
            "no_floors": self.validated_data.get("no_floors", ""),
            "no_bedrooms": self.validated_data.get("no_bedrooms", ""),
            "other": self.validated_data.get("other", ""),
            "agreement": self.validated_data.get("agreement", ""),
            "installation_type": self.validated_data.get("installation_type", ""),
            "standalone_installation": self.validated_data.get("standalone_installation", ""),
            "spare_way": self.validated_data.get("spare_way", ""),
            "roof_style": self.validated_data.get("roof_style", ""),
            "b_no_panels": self.validated_data.get("b_no_panels", ""),
            "width": self.validated_data.get("width", ""),
            "height": self.validated_data.get("height", ""),
            "panels_count": self.validated_data.get("panels_count", ""),
            "fitting": self.validated_data.get("fitting", ""),
            "mount_style_no": self.validated_data.get("mount_style_no", ""),
            "rails_count": self.validated_data.get("rails_count", ""),
            "rails_length": self.validated_data.get("rails_length", ""),
            "cable_length": self.validated_data.get("cable_length", ""),
            "storage_system_size": self.validated_data.get("storage_system_size", ""),
            "storage_cost_option": self.validated_data.get("storage_cost_option", ""),
            "help_with": self.validated_data.get("help_with", ""),
            "completed": self.validated_data.get("completed", ""),
            "total_cost": self.validated_data.get("total_cost", ""),
            "phone": self.validated_data.get("phone", ""),
        }


    def create(self, request):
        data = self.get_cleaned_data()

        product_slug = self.validated_data.get("selected_panel")
        selected_product = Product.cache_by_slug(product_slug)

        if selected_product:
            logging.debug("using cached data to get the selected panel: %s " % selected_product)
        else:
            selected_product = Product.objects.filter(slug=selected_product).first()
        

        inverter_slug = self.validated_data.get("inverter")
        selected_inverter = Inverter.cache_by_slug(inverter_slug)

        if selected_inverter:
            logging.debug("using cached data to get the selected inverter: %s " % selected_inverter)
        else:
            selected_inverter = Inverter.objects.filter(slug=selected_inverter).first()
        
        quote = Quote(**data, selected_panel=selected_product, inverter=selected_inverter, user=self.user)
        quote.save()

        cart_item = CartItem(
            cart=self.cart,
            product_id=quote.slug,
            price=self.validated_data.get("total_cost"),
            quantity=self.validated_data.get("quantity"),
            model_type=ContentType.objects.get(app_label='quote_builder', model='Quote')
        )
        cart_item.save()

        if self.validated_data.get("completed") is False:
            print("Adding to Cart")

        return quote


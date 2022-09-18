import logging
from cart.models import CartItem
from phonenumber_field.serializerfields import PhoneNumberField
from product.models import Product
from .models import Quote
from rest_framework import serializers



class QuoteBuilderSerializer(serializers.Serializer):    
    selected_panel = serializers.CharField(required=True)
    inverter = serializers.CharField(required=True)
    full_name = serializers.CharField(required=False)
    address = serializers.CharField(required=False)
    postcode = serializers.IntegerField(required=False)
    email = serializers.EmailField(required=False)
    property_type = serializers.CharField(required=True)
    no_floors = serializers.IntegerField(required=True)
    no_bedrooms = serializers.IntegerField(required=True)
    phone = PhoneNumberField()
    bill_rate = serializers.CharField(required=False)
    roof_style = serializers.CharField(required=False)
    roof_width = serializers.FloatField(required=False, default=0.0)
    roof_height = serializers.FloatField(required=False, default=0.0)
    panels_count = serializers.IntegerField(required=False, default=0)
    fitting = serializers.CharField(required=False)
    rail = serializers.CharField(required=False)
    cable_length_bat_inv = serializers.FloatField(required=False, default=0.0)
    cable_length_panel_cons = serializers.FloatField(required=False, default=0.0)
    storage_cable = serializers.FloatField(required=False, default=0.0)
    storage_system_size = serializers.CharField(required=False)
    extra_requirements = serializers.CharField(required=False)
    #total_cost = serializers.FloatField(default=0.0)
    

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
            "phone": self.validated_data.get("phone", ""),
            "roof_style": self.validated_data.get("roof_style", ""),
            "roof_width": self.validated_data.get("roof_width", ""),
            "roof_height": self.validated_data.get("roof_height", ""),
            "panels_count": self.validated_data.get("panels_count", ""),
            "fitting": self.validated_data.get("fitting", ""),
            "cable_length_bat_inv": self.validated_data.get("cable_length_bat_inv", ""),
            "cable_length_panel_cons": self.validated_data.get("cable_length_panel_cons", ""),
            "storage_cable": self.validated_data.get("storage_cable", ""),
            "storage_system_size": self.validated_data.get("storage_system_size", ""),
            "extra_requirement": self.validated_data.get("extra_requirement", ""),
            #"total_cost": self.validated_data.get("total_cost", ""),
            "inverter": self.validated_data.get("inverter", "")
        }


    def create(self, request):
        data = self.get_cleaned_data()

        product_slug = self.validated_data.get("selected_panel")
        selected_product = Product.cache_by_slug(product_slug)

        if selected_product:
            logging.debug("using cached data to get the selected panel: %s " % selected_product)
        else:
            selected_product = Product.objects.filter(slug=selected_product).first()
        
        quote = Quote(**data, selected_panel=selected_product, user=self.user)
        quote.save()

        """cart = self.cart.cache_by_slug(self.user.username)
        if cart:
            print("using cached data")
        else:
            cart = self.cart

        cart_item = CartItem(
            cart=cart,
            product_id=quote.slug,
            price=self.validated_data.get("total_cost"),
            #quantity=self.validated_data.get("quantity"),
            content_object=quote
        )
        cart_item.save()"""

        return quote


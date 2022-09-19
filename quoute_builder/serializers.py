import math
from product.models import ProductVariant
from cart.models import CartItem
from .models import Quote, Service, StorageSystem
from rest_framework import serializers



class QuoteBuilderSerializer(serializers.Serializer):    
    selected_panel = serializers.CharField(required=True)
    inverter = serializers.CharField(required=True)
    full_name = serializers.CharField(required=False)
    address = serializers.CharField(required=False)
    postcode = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    property_type = serializers.CharField(required=True)
    no_floors = serializers.IntegerField(required=True)
    no_bedrooms = serializers.IntegerField(required=True)
    phone = serializers.CharField(required=False)
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
    storage_system = serializers.CharField(required=False)
    extra_service = serializers.CharField(required=False)
    

    def __init__(self, *args, **kwargs):
        super(QuoteBuilderSerializer, self).__init__(*args, **kwargs)
        self.request = self.context.get("request")
        self.user = getattr(self.request, "user", None)
        self.cart = self.user.cart

    
    def get_cleaned_data(self):
        extra_service_id = self.validated_data.get("extra_service")
        storage_system_id = self.validated_data.get("storage_system")
        roof_height = self.validated_data.get("roof_height", "")
        roof_width = self.validated_data.get("roof_width", "")
        panels_count = self.validated_data.get("panels_count", "")
        

        selected_panel = ProductVariant.cache_by_slug(self.validated_data.get("selected_panel"))
        inverter = ProductVariant.cache_by_slug(self.validated_data.get("inverter"))

        rows = roof_height/float(selected_panel.height)

        if (panels_count * float(selected_panel.width)) < 3.3:
            rail_length = round((rows*2) * 3.3, 2)
        else:
            rail_length = round((rows*2) * 4.4, 2)

        context = {
            "full_name": self.validated_data.get("full_name", ""),
            "address": self.validated_data.get("address", ""),
            "postcode": self.validated_data.get("postcode", ""),
            "email": self.validated_data.get("email", ""),
            "property_type": self.validated_data.get("property_type", ""),
            "no_floors": self.validated_data.get("no_floors", ""),
            "no_bedrooms": self.validated_data.get("no_bedrooms", ""),
            "phone": self.validated_data.get("phone", ""),
            "roof_style": self.validated_data.get("roof_style", ""),
            "roof_width": roof_width,
            "roof_height": roof_height,
            "panels_count": self.validated_data.get("panels_count", ""),
            "fitting": self.validated_data.get("fitting", ""),
            "cable_length_bat_inv": self.validated_data.get("cable_length_bat_inv", ""),
            "panels_count": panels_count,
            "storage_cable": self.validated_data.get("storage_cable", ""),
            "inverter": inverter,
            "selected_panel": selected_panel,
            "rail_length": rail_length,
        }

        if extra_service_id is not None:
            extra_service = Service.cache_by_slug(int(extra_service_id))
            context['extra_service'] = extra_service

        if storage_system_id is not None:
            storage_system = StorageSystem.cache_by_slug(int(storage_system_id))
            context['storage_system'] = storage_system
        
        panel_price = (float(selected_panel.price) * float(panels_count)) + float(selected_panel.shipping_price)
        inverter_price = inverter.price + inverter.shipping_price

        if extra_service_id:
            if extra_service.service_title == 'Complete Installation':
                storage_syste_price = math.fsum(selected_panel.price, inverter.price)
            elif extra_service.service_title != 'Complete Installation':
                extra_service_fee = extra_service.service_price = [float(s) for s in extra_service.service_price.split() if s.isdigit()][0]
        else:
            extra_service_fee = 0.0

        
        if storage_system:
            storage_syste_price = storage_system.storage_price
        else:
            storage_syste_price = 0.0

        total_cost = sum([float(panel_price), float(inverter_price), float(extra_service_fee), float(storage_syste_price)])
        
        if total_cost:
            context['total_cost'] = round(total_cost, 2)
        
        return context


    def create(self, request):
        data = self.get_cleaned_data()

        quote = Quote(**data, user=self.user)
        quote.save()

        # convert quote into cartitem for payment process
        cart = self.cart.cache_by_slug(self.user.username)

        if cart is None:
            cart = self.cart
        
        cart_item = CartItem(
            cart=cart,
            product_id=quote.slug,
            price=data['total_cost'],
            quantity=1,
            content_object=quote
        )
        cart_item.save()
        return quote



class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = "__all__"


class StorageSystemSerializer(serializers.ModelSerializer):
    class Meta:
        model = StorageSystem
        fields = "__all__"
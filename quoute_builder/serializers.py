import math
from product.models import ProductVariant
from cart.models import CartItem
from .models import Quote, Service, StorageSystem
from rest_framework import serializers



class QuoteBuilderSerializer(serializers.Serializer):
    slug = serializers.CharField(read_only=True)
    selected_panel = serializers.CharField(required=True)
    inverter = serializers.CharField(required=True)
    full_name = serializers.CharField(required=False, allow_blank=True)
    address = serializers.CharField(required=False, allow_blank=True)
    postcode = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    property_type = serializers.CharField(required=True)
    no_floors = serializers.IntegerField(required=True)
    no_bedrooms = serializers.IntegerField(required=True)
    phone = serializers.CharField(required=False, allow_blank=True)
    bill_rate = serializers.CharField(required=False, allow_blank=True)
    roof_style = serializers.CharField(required=False, allow_blank=True)
    roof_width = serializers.FloatField(required=False, default=0.0)
    roof_height = serializers.FloatField(required=False, default=0.0)
    panels_count = serializers.IntegerField(required=False, default=0)
    fitting = serializers.CharField(required=False, allow_blank=True)
    rail = serializers.CharField(required=False, allow_blank=True)
    cable_length_bat_inv = serializers.FloatField(required=False, default=0.0)
    cable_length_panel_cons = serializers.FloatField(required=False, default=0.0)
    storage_cable = serializers.FloatField(required=False, default=0.0)
    storage_system = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    extra_service = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    

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
        fitting = ProductVariant.cache_by_slug(self.validated_data.get('fitting'))

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
            "fitting": fitting,
            "cable_length_bat_inv": self.validated_data.get("cable_length_bat_inv", ""),
            "cable_length_panel_cons": self.validated_data.get("cable_length_panel_cons", ""),
            "panels_count": panels_count,
            "storage_cable": self.validated_data.get("storage_cable", ""),
            "inverter": inverter,
            "selected_panel": selected_panel,
            "rail_length": rail_length,
        }

        if extra_service_id is not None:
            extra_service = Service.cache_by_slug(int(extra_service_id))
            context['extra_service'] = extra_service          

            if extra_service.service_title == 'Complete Installation':
                extra_service_fee = (math.fsum([panel_price, inverter.price, fitting_price, storage_system_price])) * 2
                
            elif extra_service.service_title != 'Complete Installation':
                extra_service_fee = [float(s) for s in extra_service.service_price.split() if s.isdigit()][0]

        else:
            extra_service_fee = 0.0

        if storage_system_id is not None:
            storage_system = StorageSystem.cache_by_slug(int(storage_system_id))
            storage_system_price = storage_system.storage_price

            context['storage_system'] = storage_system
        else:
            storage_system_price = 0.0
        
        panel_price = (float(selected_panel.price) * float(panels_count))
        inverter_price = inverter.price
        fitting_price = fitting.price

        sum_cost = sum([float(panel_price), float(inverter_price), float(fitting_price), float(extra_service_fee), float(storage_system_price)])

        if self.validated_data.get('panels_count') > 20:
            total_cost = sum([sum_cost, (sum_cost * 0.2), 300])
            context['shipping_price'] = 300
        else:
            total_cost = sum([sum_cost, (sum_cost * 0.2), 200])
            context['shipping_price'] = 200

        if total_cost:
            context['total_cost'] = round(total_cost)
        
        context['equipment_cost'] = sum([float(panel_price), float(inverter_price), float(fitting_price), float(storage_system_price)])
        
        return context

    def create(self, request):
        data = self.get_cleaned_data()

        quote = Quote(**data, user=self.user)
        quote.save()

        # notify user about the quote
        quote.confirmation()

        # convert quote into cartitem for payment process
        cart = self.cart.cache_by_slug(self.user.username)

        if cart is None:
            cart = self.cart
        
        cart_item = CartItem(
            cart=cart,
            product_id=quote.slug,
            total_cost=data['total_cost'],
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


class QuoteSerializer(serializers.ModelSerializer):
    panel_image = serializers.FileField(source='selected_panel.image', read_only=True)
    inverter_image = serializers.FileField(source='inverter.image', read_only=True)
    fitting_image = serializers.FileField(source='fitting.image', read_only=True)
    panel_wattage = serializers.CharField(source='selected_panel.wattage', read_only=True)
    inverter_wattage = serializers.CharField(source='inverter.wattage', read_only=True)
    panel_title = serializers.CharField(source='selected_panel.title', read_only=True)
    inverter_title = serializers.CharField(source='inverter.title', read_only=True)
    fitting_title = serializers.CharField(source='fitting.title', read_only=True)
    panel_price = serializers.CharField(source='selected_panel.price', read_only=True)
    inverter_price = serializers.CharField(source='inverter.price', read_only=True)
    fitting_price = serializers.CharField(source='fitting.price', read_only=True)
    service_title = serializers.CharField(source='extra_service.service_title', read_only=True)
    service_price = serializers.CharField(source='extra_service.service_price', read_only=True)

    class Meta:
        model = Quote
        fields = "__all__"
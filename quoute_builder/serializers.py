from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers

from .models import Quote


class QuoteBuilderSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(max_length=150, required=True)
    address = serializers.CharField(required=True)
    postcode = serializers.IntegerField(min_val=0, required=True)
    email = serializers.EmailField(required=True)
    phone = PhoneNumberField(required=True)
    property_type = serializers.CharField(max_length=50, required=True)
    no_floors = serializers.IntegerField(min_val=1, required=True)
    no_bedrooms = serializers.IntegerField(min_val=1, required=True)
    other = serializers.CharField(required=False)
    bill_rate = serializers.CharField(required=False)
    agreement = serializers.BooleanField(default=False)
    installation_type = serializers.CharField(max_length=150, required=True) # on a roof or standalone
    standalone_installation = serializers.CharField(max_length=70, required=False)
    single_phase = serializers.BooleanField(default=False)
    spare_way = serializers.BooleanField(default=False)
    roof_style = serializers.CharField(max_length=20, required=False)
    b_no_panels = serializers.CharField(required=False) # yes or no
    width = serializers.IntegerField(min_val=1, required=False)
    height = serializers.IntegerField(min_val=1, required=False)
    selected_panel_id = serializers.CharField(max_legth=200, required=False)
    panels_count = serializers.IntegerField(max_length=1, required=False)
    fitting = serializers.CharField(required=False)
    mount_style_no = serializers.CharField(max_length=200, required=False)
    rails_count = serializers.IntegerField(min_val=1, required=False)
    rails_length = serializers.FloatField(required=False) #2.2M or 3.3M
    cable_length = serializers.FloatField(required=False)
    storage_system_size = serializers.CharField(required=False)
    storage_cost_option = serializers.CharField(required=False)
    help_with = serializers.CharField(required=False)

    class Meta:
        model = Quote
        fields = [
            "id",
            "full_name",
            "address",
            "postcode",
            "email",
            "phone",
            "property_type",
            "no_bedrooms",
            "bill_rate",
            "other",
            "agreement",
            "installation_type",
            "standalone_installation",
            "single_phase",
            "spare_way",
            "roof_style",
            "b_no_panels",
            "width",
            "height",
            "panels_count",
            "fitting",
            "mount_style_no",
            "rails_count",
            "rails_length",
            "storage_system_size",
            "storage_cost_option",
            "help_with",
        ]
    

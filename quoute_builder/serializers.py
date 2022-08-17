from phonenumber_field.serializerfields import PhoneNumberField
from .models import Quote
from rest_framework import serializers



class QuoteBuilderSerializer(serializers.ModelSerializer):    
    product = serializers.SlugRelatedField(slug_field="title", read_only=True)
    full_name = serializers.CharField(required=True)
    address = serializers.CharField(required=True)
    postcode = serializers.IntegerField(required=True)
    email = serializers.EmailField(required=True)
    property_type = serializers.CharField(required=True)
    no_floors = serializers.IntegerField(required=True)
    no_bedrooms = serializers.IntegerField(required=True)
    other = serializers.CharField(required=False)
    bill_rate = serializers.CharField(required=False)
    agreement = serializers.BooleanField(default=False)
    installation_type = serializers.CharField(required=True) # on a roof or standalone
    standalone_installation = serializers.CharField(required=False)
    spare_way = serializers.BooleanField(default=False)
    roof_style = serializers.CharField(required=False)
    b_no_panels = serializers.CharField(required=False) # yes or no
    width = serializers.IntegerField(required=False)
    height = serializers.IntegerField(required=False)
    panels_count = serializers.IntegerField(required=False)
    fitting = serializers.CharField(required=False)
    mount_style_no = serializers.CharField(required=False)
    rails_count = serializers.IntegerField(required=False)
    rails_length = serializers.FloatField(required=False) #2.2M or 3.3M
    cable_length = serializers.FloatField(required=False)
    storage_system_size = serializers.CharField(required=False)
    storage_cost_option = serializers.CharField(required=False)
    help_with = serializers.CharField(required=False)

    class Meta:
        model = Quote
        fields = "__all__"
       
    def __init__(self, *args, **kwargs):
        super(QuoteBuilderSerializer, self).__init__(*args, **kwargs)

        self.request = self.context.get("request")
        self.user = getattr(self.request, "user", None)
    
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
        }


    def create_quote(self, quote, validated_data):
        quote.product = self.validated_data.get("product")
        quote.user = self.user
        quote.save()

    def perform_create(self, request, quote):
        self.create_quote(quote, self.get_cleaned_data())
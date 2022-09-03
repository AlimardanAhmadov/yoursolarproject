from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from .models import CartItem
from product.models import ProductVariant


class CartItemSerializer(serializers.Serializer):
    quantity = serializers.CharField(write_only=True)
    variant_slug = serializers.CharField(write_only=True)

    def __init__(self, *args, **kwargs):
        super(CartItemSerializer, self).__init__(*args, **kwargs)

        self.request = self.context.get("request")
        self.product = self.context.get("product")
        self.cart = self.context.get("cart")
        self.user = getattr(self.request, "user", None)
    
    def get_variant(self, attrs):
        selected_variant = ProductVariant.cache_by_slug(attrs['variant_slug'])
        if not selected_variant:
            selected_variant = ProductVariant.objects.filter(slug=attrs['variant_slug'], selected_product=self.product).first()

        return selected_variant

    def validate(self, attrs):
        cart_item = CartItem.objects.filter(cart=self.cart).exists()
        if cart_item:
            raise serializers.ValidationError(
                {"cart": 'You already have this item in your shopping cart'}
            )

        quantity = self.get_variant(attrs).quantity
        quantity_match = (
            int(attrs["quantity"]) > quantity,
        )
        quantity_min = (
            int(attrs["quantity"]) < 1,
        )

        if all(quantity_match):
            raise serializers.ValidationError(
                {"quantity": 'You cannot order more than %s of this item' % quantity}
            )
        
        if all(quantity_min):
            raise serializers.ValidationError(
                {"min quantity": 'You cannot order less than 1 item'}
            )

        return attrs    


    def create(self, attrs):
        selected_variant=self.get_variant(attrs)

        new_cart_item = CartItem.objects.create(
            cart=self.cart,
            quantity=self.validated_data.get("quantity"),
            price=self.get_variant(attrs).price,
            product_id=self.product.slug,
            variant_id=self.get_variant(attrs).slug,
            content_object=selected_variant
        )
        
        return new_cart_item


class UpdateCartSerializer(serializers.Serializer):
    quantity = serializers.IntegerField()

    def __init__(self, *args, **kwargs):
        super(UpdateCartSerializer, self).__init__(*args, **kwargs)

        self.request = self.context["request"]
        self.item = self.context.get("product")

    def validate(self, attrs):
        quantity = self.item.content_object.quantity
        quantity_match = (
            attrs["quantity"] > quantity,
        )

        if all(quantity_match):
            raise serializers.ValidationError(
                {"quantity": 'You cannot order more than %s of this item' % quantity}
            )
        
        return attrs
    
    def create(self, validated_data):
        cart_item = self.item
        cart_item.quantity = self.validated_data.get('quantity')
        cart_item.save()

        return cart_item


class CartDetailsItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ('slug',)


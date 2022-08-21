from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _
from .models import Cart, CartItem
from product.models import ProductVariant


class CartItemSerializer(serializers.Serializer):
    quantity = serializers.IntegerField()
    price = serializers.FLoatField()
    slug = serializers.SlugField()

    def __init__(self, *args, **kwargs):
        super(CartItemSerializer, self).__init__(*args, **kwargs)

        self.request = self.context["request"]
        self.product = self.context["product"]
        self.cart = self.context["cart"]
        self.user = getattr(self.request, "user", None)
    
    def get_variant(self, attrs):
        selected_variant = ProductVariant.cache_by_slug(attrs['slug'])
        if not selected_variant:
            selected_variant = ProductVariant.objects.filter(slug=attrs['slug'], product=self.product).first()

        return selected_variant

    def validate(self, attrs):
        cart_item = CartItem.objects.filter(cart=self.cart).exists()
        if cart_item:
            raise serializers.ValidationError(
                {"cart": 'You already have this item in your shopping cart'}
            )

        quantity = self.get_variant(self, attrs).quantity
        quantity_match = (
            attrs["quantity"] > quantity,
        )

        if all(quantity_match):
            raise serializers.ValidationError(
                {"quantity": 'You cannot order more than %s of this item' % quantity}
            )

        return attrs    


    def create(self, attrs):
        selected_variant=self.get_variant(self, attrs)

        new_cart_item =CartItem.objects.create(
            cart=self.cart,
            quantity=self.validated_data.get("quantity"),
            price=self.validated_data.get("price"),
            product_id=self.product.slug,
            content_object=selected_variant
        )
        
        return new_cart_item


class UpdateCartSerializer(serializers.Serializer):
    quantity = serializers.IntegerField()

    def __init__(self, *args, **kwargs):
        super(UpdateCartSerializer, self).__init__(*args, **kwargs)

        self.request = self.context["request"]
        self.item = self.context["item"]
    

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
    

    def create(self, attrs):
        cart_item = self.item
        cart_item.quantity = attrs['quantity']
        cart_item

        return cart_item
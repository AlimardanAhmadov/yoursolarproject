from rest_framework import serializers
from .models import Product, ProductVariant


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"


class ProductVariantSerializer(serializers.ModelSerializer):
    product_slug = serializers.CharField(source='selected_product.slug', read_only=True)
    title = serializers.CharField(source='selected_product.title', read_only=True)
    brand = serializers.CharField(source='selected_product.brand', read_only=True)
    shipping_policy = serializers.CharField(source='selected_product.shipping_policy', read_only=True)
    return_policy = serializers.CharField(source='selected_product.return_policy', read_only=True)
    category = serializers.CharField(source='selected_product.category', read_only=True)
    
    class Meta:
        model = ProductVariant
        fields = ['primary_variant', 'category', 'width', 'height', 'shipping_policy', 'return_policy', 'product_slug', 'title', 'brand', 'image', 'price', 'discount', 'sku', 'active', 'slug', 'quantity', 'description']
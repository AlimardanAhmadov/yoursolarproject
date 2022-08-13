from django.contrib import admin
from .models import Product, ProductVariant



class VariantInline(admin.StackedInline):
    model = ProductVariant
    extra = 0
    fields = ['primary_variant', 'price', 'discount', 'sku', 'active']

class ProductAdmin(admin.ModelAdmin):
    inlines = [VariantInline]

admin.site.register(Product, ProductAdmin)
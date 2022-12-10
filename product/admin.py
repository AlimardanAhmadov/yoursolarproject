from django.contrib import admin
from .models import Product, ProductVariant

class VariantInline(admin.StackedInline):
    model = ProductVariant
    extra = 0
    fields = ['primary_variant', 'title', 'shipping_price', 'image', 'availability', 'cable_size', 'suitable_roof_style', 'price', 'discount', 'width', 'height', 'wattage', 'sku', 'active', 'slug', 'quantity', 'description']
    
class ProductAdmin(admin.ModelAdmin):
    inlines = [VariantInline]
    search_fields = ['slug', 'title',]
    list_display = ('title', 'brand', 'category')

admin.site.register(Product, ProductAdmin)
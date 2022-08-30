from django.contrib import admin
from .models import Product, ProductVariant



class VariantInline(admin.StackedInline):
    model = ProductVariant
    extra = 0
    fields = ['primary_variant', 'price', 'discount', 'sku', 'active', 'slug', 'quantity']

class ProductAdmin(admin.ModelAdmin):
    inlines = [VariantInline]
    list_display = ('title', 'brand', 'category', 'availability')

admin.site.register(Product, ProductAdmin)
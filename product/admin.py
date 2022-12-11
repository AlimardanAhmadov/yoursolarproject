from django.contrib import admin
from django.utils.text import slugify
from .models import Product, ProductVariant
from main.utils import id_generator


def duplicate_event(modeladmin, request, queryset):
    for object in queryset:
        old_object = object
        variants = ProductVariant.objects.filter(selected_product=old_object)

        print(old_object)
        object.id = None
        object.save()

        variants_array = []

        print(variants)

        for product in variants:
            variant = ProductVariant(
                selected_product = object,
                title = product.title,
                primary_variant = product.primary_variant,
                description = product.description,
                availability = product.availability,
                width = product.width,
                height = product.height,
                materials = product.materials,
                price = product.price,
                discount = product.discount,
                image = product.image,
                sku = product.sku,
                active = product.active,
                quantity = product.quantity,
                shipping_price = product.shipping_price,
                size = product.size,
                suitable_roof_style = product.suitable_roof_style,
                wattage = product.wattage,
                cable_size = product.cable_size,
                slug = slugify(str(id_generator()))
            )
            variants_array.append(variant)
        
        ProductVariant.objects.bulk_create(variants_array)

            # variant.selected_product = object
            # variant.title = product.title
            # variant.primary_variant = product.primary_variant
            # variant.description = product.description
            # variant.availability = product.availability
            # variant.width = product.width
            # variant.height = product.height
            # variant.materials = product.materials
            # variant.price = product.price
            # variant.discount = product.discount
            # variant.image = product.image
            # variant.sku = product.sku
            # variant.active = product.active
            # variant.quantity = product.quantity
            # variant.shipping_price = product.shipping_price
            # variant.size = product.size
            # variant.suitable_roof_style = product.suitable_roof_style
            # variant.wattage = product.wattage
            # variant.cable_size = product.cable_size
            

duplicate_event.short_description = "Duplicate selected record"

class VariantInline(admin.StackedInline):
    model = ProductVariant
    extra = 0
    fields = ['primary_variant', 'title', 'shipping_price', 'image', 'availability', 'cable_size', 'suitable_roof_style', 'price', 'discount', 'width', 'height', 'wattage', 'sku', 'active', 'slug', 'quantity', 'description']
    
class ProductAdmin(admin.ModelAdmin):
    inlines = [VariantInline]
    search_fields = ['slug', 'title',]
    list_display = ('title', 'brand', 'category')
    actions=[duplicate_event, ]


admin.site.register(Product, ProductAdmin)
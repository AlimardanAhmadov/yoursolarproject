from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.StackedInline):
    model = OrderItem
    extra = 0
    fields = ('order', 'order_product_id', 'total', 'product_title', 'product_quantity')


class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]
    list_display = ('user', 'order_number', 'status', 'total', 'slug', 'address', 'secondary_address', 'created')


admin.site.register(Order, OrderAdmin)
from django.contrib import admin
from .models import Cart, CartItem


class CartAdmin(admin.ModelAdmin):
    search_fields = ['slug', ]
    search_help_text = 'Search by cart title'

admin.site.register(CartItem)
admin.site.register(Cart, CartAdmin)
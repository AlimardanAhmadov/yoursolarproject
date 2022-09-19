from django.contrib import admin
from .models import Quote, Service, StorageSystem


class QuoteAdmin(admin.ModelAdmin):
    search_fields = ['slug', 'title',]
    list_display = [field.name for field in Quote._meta.get_fields()]


class ServiceAdmin(admin.ModelAdmin):
    list_display = ('service_title', 'service_price')

class StorageAdmin(admin.ModelAdmin):
    list_display = ('storage_size', 'storage_price')

admin.site.register(Quote, QuoteAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(StorageSystem, StorageAdmin)
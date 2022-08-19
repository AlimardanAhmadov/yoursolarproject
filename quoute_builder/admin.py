from django.contrib import admin
from .models import Quote


class QuoteAdmin(admin.ModelAdmin):
    search_fields = ['slug', 'title',]

admin.site.register(Quote, QuoteAdmin)

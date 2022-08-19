from django.contrib.gis.geoip2 import GeoIP2
from django.conf import settings

def geoip(request):
    if settings.DEBUG == False:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        
        g = GeoIP2()
        location = g.city(ip)
        location_country = location["country_name"]
        context = {
            "location_country": location_country,
        }

        return context
    else:
        return {}
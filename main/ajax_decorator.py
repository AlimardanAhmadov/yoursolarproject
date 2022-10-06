import json
from functools import wraps
from cart.models import Cart
from django.http import HttpResponse

def ajax_login_required(view):
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        cart = Cart.objects.all().exists()
        if not cart:
            response = HttpResponse(json.dumps({'err': ["Cart doesn't exist. Please try to refresh the page or try again later."]}), 
                content_type='application/json')
            response.status_code = 400
            return response
        return view(request, *args, **kwargs)
    return wrapper
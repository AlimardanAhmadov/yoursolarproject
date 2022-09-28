import json
from functools import wraps
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse

def ajax_login_required(view):
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            
            response = HttpResponse(json.dumps({'err': ["You need to sign in or create a new account!"]}), 
                content_type='application/json')
            response.status_code = 400
            return response
        return view(request, *args, **kwargs)
    return wrapper
import re, json
from django.http import HttpResponse, JsonResponse

from rest_framework.generics import (
    ListCreateAPIView,
)
from rest_framework import permissions, status
from rest_framework.response import Response

from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required 
from django.db import transaction

from main.html_renderer import MyHTMLRenderer
from .serializers import QuoteBuilderSerializer



class QuoteBuilderView(ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    #template_name = '***'
    #renderer_classes = [MyHTMLRenderer,]
    serializer_class = QuoteBuilderSerializer

    #@method_decorator(login_required(login_url='***'))
    def dispatch(self, *args, **kwargs):
        return super(QuoteBuilderView, self).dispatch(*args, **kwargs)

    def get(self, request, format=None):
        serializer = QuoteBuilderSerializer(context={'request': request})
        return Response(data=serializer.data)

    def create(self, request, *args, **kwargs):
        with transaction.atomic():
            try:
                serializer = QuoteBuilderSerializer(data=request.data, context={'request': request})
                if serializer.is_valid():
                    self.perform_create_quote(serializer)
                    return JsonResponse(serializer.data, status=status.HTTP_200_OK)
                else:
                    data = []
                    emessage=serializer.errors 
                    print(emessage)
                    for key in emessage:
                        err_message = str(emessage[key])
                        err_string = re.search("string='(.*)', ", err_message) 
                        message_value = err_string.group(1)
                        final_message = f"{key} - {message_value}"
                        data.append(final_message)

                    response = HttpResponse(json.dumps({'err': data}), 
                        content_type='application/json')
                    response.status_code = 400
                    return response

            except Exception as exc:
                print(exc)
                transaction.set_rollback(True)
                response = HttpResponse(json.dumps({'err': ["Something went wrong!"]}), 
                    content_type='application/json')
                response.status_code = 400
                return response

    def perform_create_quote(self, serializer):
        quote = serializer.save()
        return quote
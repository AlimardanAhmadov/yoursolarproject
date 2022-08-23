from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework.response import Response
from main.html_renderer import MyHTMLRenderer


def index(request):
    return render(request, 'main/base.html')


class EShopAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    template_name = 'user/profile.html'
    renderer_classes = [MyHTMLRenderer, ]

    def dispatch(self, *args, **kwargs):
        return super(EShopAPIView, self).dispatch(*args, **kwargs)

    def get(self, request):
        
        return "pk"
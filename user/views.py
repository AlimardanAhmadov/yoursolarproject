import re, json
from django.db import transaction
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import get_user_model
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters
from django.contrib.auth.decorators import login_required 
from rest_framework.response import Response
from allauth.account.models import EmailAddress, EmailConfirmationHMAC
from rest_framework.renderers import TemplateHTMLRenderer
from rest_auth.utils import jwt_encode 
from rest_auth.serializers import PasswordResetConfirmSerializer
from rest_auth.app_settings import JWTSerializer
from rest_framework import permissions, status
from rest_auth.views import (
    LoginView,
)
from rest_framework.generics import (
    ListCreateAPIView,
    GenericAPIView
)

from .models import Customer
from .send_mail import send_register_mail, send_reset_password_email
from .serializers import (ChangePasswordSerializer, CustomRegisterSerializer, SendResetPasswordSerializer, GoogleSocialAuthSerializer)

User = get_user_model()

sensitive_post_parameters_m = method_decorator(
    sensitive_post_parameters("password1", "password2")
)

def get_prev_url(request):
    try:
        prev_url = request.META.get('HTTP_REFERER')
        sep = '?next='
        stripped = prev_url.split(sep, 1)[1]
    except Exception:
        stripped = None
    return stripped


class MyHTMLRenderer(TemplateHTMLRenderer):
    def get_template_context(self, *args, **kwargs):
        context = super().get_template_context(*args, **kwargs)
        if isinstance(context, list):
            context = {"items": context}
        return context

class LoginAPIView(LoginView):
    queryset = ""
    #template_name = ""
    allowed_methods = ("POST", "OPTIONS", "HEAD", "GET")

    def get_response(self, request):
        serializer_class = self.get_response_serializer()
        if getattr(settings, "REST_USE_JWT", False):
            data = {"user": self.user, "token": self.token}
            serializer = serializer_class(
                instance=data, context={"request": self.request}
            )
        else:
            serializer = serializer_class(
                instance=self.token, context={"request": self.request}
            )
        context = {
            'data': serializer.data,
            'status': status.HTTP_200_OK,
        }
        if get_prev_url(request) is not None:
            next_url = get_prev_url(request)
            context['next_url'] = next_url
        response = JsonResponse(context)

        return response

    def post(self, request, *args, **kwargs):
        self.request = request
        self.serializer = self.get_serializer(
            data=self.request.data, context={"request": request}
        )
        if self.serializer.is_valid():
            self.login()
        else:
            data = []
            emessage=self.serializer.errors 
            print(emessage)
            for key in emessage:
                err_message = str(emessage[key])
                print(err_message)
                err_string = re.search("string=(.*), ", err_message) 
                message_value = err_string.group(1)
                final_message = f"{message_value}"
                data.append(final_message)

            response = HttpResponse(json.dumps({'error': data}), 
                content_type='application/json')
            response.status_code = 400
            return response
        return self.get_response(request)


class RegisterAPIView(ListCreateAPIView):
    #renderer_classes = [MyHTMLRenderer,]
    #template_name = "user/signup.html"
    queryset = Customer.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = CustomRegisterSerializer
    
    
    @sensitive_post_parameters_m
    def dispatch(self, *args, **kwargs):
        return super(RegisterAPIView, self).dispatch(*args, **kwargs)

    def get(self, request, format=None):
        users = User.objects.all()
        serializer = CustomRegisterSerializer(users, many=True)
        return Response(serializer.data)

    def get_serializer(self, *args, **kwargs):
        return CustomRegisterSerializer(*args, **kwargs)

    def get_response_data(self, user):
        data = {"user": user, "token": self.token}
        return JWTSerializer(data).data

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = self.perform_create(serializer)
            if getattr(settings, "REST_USE_JWT", False):
                self.token = jwt_encode(user)
            return JsonResponse(serializer.data, status=status.HTTP_200_OK)
        else:
            data = []
            emessage=serializer.errors 
            for key in emessage:
                err_message = str(emessage[key])
                print(err_message)
                err_string = re.search("string=(.*), code", err_message)
                message_value = err_string.group(1)
                final_message = f"{key} - {message_value}"
                data.append(final_message)

            response = HttpResponse(json.dumps({'error': data}), 
                content_type='application/json')
            response.status_code = 400
            return response

    def perform_create(self, serializer):
        user = serializer.save(self.request)
        if getattr(settings, "REST_USE_JWT", False):
            self.token = jwt_encode(user)

        email = EmailAddress.objects.get(email=user.email, user=user)
        confirmation = EmailConfirmationHMAC(email)
        key = confirmation.key
        #send_register_mail.delay(user.id, key)
        print("account-confirm-email/" + key)
        return user


class PasswordResetView(ListCreateAPIView):
    permission_classes = (permissions.AllowAny,)
    allowed_methods = ("POST", "OPTIONS", "HEAD", "GET")
    serializer_class = SendResetPasswordSerializer


    def get_serializer(self, *args, **kwargs):
        return SendResetPasswordSerializer(*args, **kwargs)

    def get(self, request):
        serializer = SendResetPasswordSerializer(context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            if serializer.is_valid():
                email = request.data.get("email", None)
                
                try:
                    user = User.objects.get(email=email)
                    send_reset_password_email.delay(user.pk)
                except User.DoesNotExist:
                    response = HttpResponse(json.dumps({'err': ['Please enter a valid email']}), 
                        content_type='application/json')
                    response.status_code = 400
                    return response
                return Response(
                    {"detail": _("Password reset e-mail has been sent.")},
                    status=status.HTTP_200_OK,
                )
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
        except Exception:
            response = HttpResponse(json.dumps({'err': ['Something went wrong']}), 
                        content_type='application/json')
            response.status_code = 400
            return response



class PasswordResetConfirmView(ListCreateAPIView):
    #renderer_classes = [MyHTMLRenderer,]
    #template_name = ""
    permission_classes = (permissions.AllowAny,)
    serializer_class = PasswordResetConfirmSerializer

    @sensitive_post_parameters_m
    def dispatch(self, *args, **kwargs):
        return super(PasswordResetConfirmView, self).dispatch(*args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        serializer = PasswordResetConfirmSerializer(context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def get_serializer(self, *args, **kwargs):
        return PasswordResetConfirmSerializer(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
            except User.DoesNotExist:
                response = HttpResponse(json.dumps({'err': ['Something went wrong!']}), 
                    content_type='application/json')
                response.status_code = 400
                return response
            return JsonResponse({'data':serializer.data, 'status':status.HTTP_200_OK})
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


class ChangePasswordView(ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    template_name = 'coach/edit_profile.html'
    renderer_classes = [MyHTMLRenderer,]
    serializer_class = ChangePasswordSerializer

    @method_decorator(login_required(login_url='***'))
    @sensitive_post_parameters_m
    def dispatch(self, *args, **kwargs):
        return super(ChangePasswordView, self).dispatch(*args, **kwargs)

    def get(self, request, format=None):
        user = self.request.user
        serializer = ChangePasswordSerializer(user, context={'request': request})
        return Response(data=serializer.data)

    def create(self, request, *args, **kwargs):
        with transaction.atomic():
            try:
                user = self.request.user
                serializer = ChangePasswordSerializer(user, data=request.data, context={'request': request})
                if serializer.is_valid():
                    user.set_password(request.data.get("password"))
                    user.save()
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
                response = HttpResponse(json.dumps({'err': data}), 
                    content_type='application/json')
                response.status_code = 400
                return response


class GoogleSocialAuthView(ListCreateAPIView):
    serializer_class = GoogleSocialAuthSerializer
    queryset = ""

    @sensitive_post_parameters_m
    def dispatch(self, *args, **kwargs):
        return super(GoogleSocialAuthView, self).dispatch(*args, **kwargs)

    def get(self, format=None):
        users = User.objects.all()
        serializer = GoogleSocialAuthSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = ((serializer.validated_data)['auth_token'])
        return Response(data, status=status.HTTP_200_OK)

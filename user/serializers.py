import os
from django.contrib.auth import get_user_model, authenticate, login
from django.conf import settings
from django.contrib.auth.forms import SetPasswordForm
from django.utils.translation import gettext_lazy as _
from allauth.account.models import EmailAddress, EmailConfirmationHMAC
from rest_framework import serializers, exceptions
from rest_framework_simplejwt.tokens import RefreshToken
from rest_auth.registration.serializers import RegisterSerializer
from user.send_mail import send_register_mail

from .models import Business, Customer
from . import google_validate

# Get the UserModel
UserModel = get_user_model()


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=False, allow_blank=True)
    password = serializers.CharField(style={"input_type": "password"})

    def authenticate(self, **kwargs):
        return authenticate(self.context["request"], **kwargs)

    def _validate_email(self, email, password):
        user = None

        if email and password:
            user = self.authenticate(email=email, password=password)
        else:
            msg = _('Must include "username" and "password".')
            raise exceptions.ValidationError(msg)

        return user

    def _validate_username(self, username, password):
        user = None

        if username and password:
            user = self.authenticate(username=username, password=password)
        else:
            msg = _(
                'Must include "username or "email" and "password".'
            )
            raise exceptions.ValidationError(msg)

        return user

    def _validate_username_email(self, username, email, password):
        user = None

        if email and password:
            user = self.authenticate(email=email, password=password)
        elif username and password:
            user = self.authenticate(username=username, password=password)
        else:
            msg = _(
                'Must include either "username" or "email" and "password".'
            )
            raise exceptions.ValidationError(msg)

        return user

    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")

        user = None

        if username:
            user = self._validate_username_email(username, "", password)

        if user:
            if not user.is_active:
                msg = _("User account is inactive.")
                raise exceptions.ValidationError(msg)
        else:
            msg = _("please check your username or password.")
            raise exceptions.ValidationError(msg)

        if "rest_auth.registration" in settings.INSTALLED_APPS:
            from allauth.account import app_settings

            if (
                app_settings.EMAIL_VERIFICATION
                == app_settings.EmailVerificationMethod.MANDATORY
            ):
                try:
                    email_address = user.emailaddress_set.get(email=user.email)
                except EmailAddress.DoesNotExist:
                    raise serializers.ValidationError(
                        _(
                            "This account doesn't have an E-mail address!, so that you can't login."
                        )
                    )
                if not email_address.verified:
                    raise serializers.ValidationError(_("E-mail is not verified."))

        attrs["user"] = user
        token = RefreshToken.for_user(attrs["user"])
        token = {
            "refresh_token": str(token),
            "access_token": str(token.access_token)
        }
        return attrs


class CustomRegisterSerializer(RegisterSerializer):
    username = serializers.CharField(required=False, write_only=True)
    first_name = serializers.CharField(required=False, write_only=True)
    last_name = serializers.CharField(required=False, write_only=True)
    email = serializers.EmailField(required=True, write_only=True)
    agreement = serializers.BooleanField(default=False)
    account_type = serializers.CharField(required=True, write_only=True)
    company_name = serializers.CharField(required=False, write_only=True)
    provider = serializers.CharField(required=True, write_only=True)


    def __init__(self, *args, **kwargs):
        super(CustomRegisterSerializer, self).__init__(*args, **kwargs)

        self.request = self.context.get("request")

    def get_cleaned_data_customer(self):
        return {
            "first_name": self.validated_data.get("first_name", ""),
            "last_name": self.validated_data.get("last_name", ""),
            "agreement": self.validated_data.get("agreement", ""),
        }
    
    def get_cleaned_data_business(self):
        return {
            "agreement": self.validated_data.get("agreement", ""),
            "company_name": self.validated_data.get("company_name", ""),
        }
    
    def validate(self, attrs):
        agreement = attrs['agreement']
        account_type = attrs['account_type']

        if agreement is not True:
            raise serializers.ValidationError({'Agreement': ['You must agree to our terms & conditions']})
        
        if account_type == 'business':
            if Business.objects.filter(company_name=attrs['company_name']).exists():
                raise serializers.ValidationError({'Company': ['A user already exists with this company name ']})
                
            if attrs['company_name'] is None:
                raise serializers.ValidationError({'Company Name': ['This field cannot be blank']})
                
        elif account_type == 'individual':
            if attrs['first_name'] is None:
                raise serializers.ValidationError({'First Name': ['This field cannot be blank']})
            elif attrs['last_name'] is None:
                raise serializers.ValidationError({'Last Name': ['This field cannot be blank']})

        return attrs

    def create_customer(self, user, validated_data):
        user.first_name = self.validated_data.get("first_name")
        user.last_name = self.validated_data.get("last_name")
        user.email = self.validated_data.get("email")
        user.username = self.validated_data.get("username")
        user.save()

        token = RefreshToken.for_user(user)
        token = {
            "refresh_token": str(token),
            "access_token": str(token.access_token)
        }

        Customer.objects.create(
            user=user,
            full_name = self.validated_data.get("first_name") + " " + self.validated_data.get("last_name"),
            provider=self.validated_data.get('provider')
        )

        if self.validated_data.get('provider') == 'Google':
            login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')

    def create_business(self, user, validated_data):
        user.email = self.validated_data.get('email')
        user.username = self.validated_data.get('company_name')
        user.save()
        
        token = RefreshToken.for_user(user)
        token = {
            "refresh_token": str(token),
            "access_token": str(token.access_token)
        }

        Business.objects.create(
            user=user, 
            company_name = self.validated_data.get('company_name'),
            provider=self.validated_data.get('provider')
        )

        if self.validated_data.get('provider') == 'Google':
            login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')

    def custom_signup(self, request, user):
        if self.validated_data.get('account_type') == 'business':
            self.create_business(user, self.get_cleaned_data_customer())
        else:
            self.create_customer(user, self.get_cleaned_data_business())


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = [
            "id",
            "username",
            "email",
            "password"
        ]

class BussinesUserSerializer(serializers.ModelSerializer):
    company_name = serializers.BooleanField(source="business.company_name")

    class Meta:
        model = get_user_model()
        fields = [
            "id",
            "email",
            "password",
            "company_name",
        ]


class SendResetPasswordSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ["email", ]


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=128)
    new_password1 = serializers.CharField(max_length=128)
    new_password2 = serializers.CharField(max_length=128)

    set_password_form_class = SetPasswordForm

    def __init__(self, *args, **kwargs):
        self.old_password_field_enabled = getattr(
            settings, "OLD_PASSWORD_FIELD_ENABLED", False
        )
        self.logout_on_password_change = getattr(
            settings, "LOGOUT_ON_PASSWORD_CHANGE", False
        )
        super(ChangePasswordSerializer, self).__init__(*args, **kwargs)

        self.request = self.context.get("request")
        self.user = getattr(self.request, "user", None)

    def validate_old_password(self, value): 
        invalid_password_conditions = (
            self.user,
            not self.user.check_password(value),
        )

        if all(invalid_password_conditions):
            raise serializers.ValidationError("Invalid password")
        return value

    def validate(self, attrs):
        self.set_password_form = self.set_password_form_class(
            user=self.user, data=attrs
        )

        old_password_match = (
            self.user,
            attrs["old_password"] == attrs["new_password1"],
        )

        if all(old_password_match):
            raise serializers.ValidationError(
                "your new password matching with old password"
            )

        if not self.set_password_form.is_valid():
            raise serializers.ValidationError(self.set_password_form.errors)
        return attrs

    def save(self):
        self.set_password_form.save()
        if not self.logout_on_password_change:
            from django.contrib.auth import update_session_auth_hash

            update_session_auth_hash(self.request, self.user)


class GoogleSocialAuthSerializer(serializers.Serializer):
    auth_token = serializers.CharField()

    def validate_auth_token(self, auth_token):
        user_data = google_validate.Google.validate(auth_token)
        try:
            user_data['sub']
        except:
            raise serializers.ValidationError(
                'Invalid TOKEN'
            )

        if user_data['aud'] != os.environ['GOOGLE_CLIENT_ID']:
            raise serializers.ValidationError("User not found")
        
        return user_data


class GoogleLoginSerializer(serializers.Serializer):
    email = serializers.CharField(required=False, allow_blank=True)

    def __init__(self, *args, **kwargs):
        super(GoogleLoginSerializer, self).__init__(*args, **kwargs)

        self.request = self.context.get("request")
    

    def _validate_email(self, email):
        user = None

        if email:
            user = UserModel.objects.filter(email=email).first()
        else:
            msg = _('Must include "email".')
            raise serializers.ValidationError(msg)

        return user
    
    def validate(self, attrs):
        email = attrs.get("email")

        user = None

        if email:
            user = self._validate_email(email)

        if user:
            if not user.is_active:
                msg = {'Error:': ['This field cannot be blank']}
                raise serializers.ValidationError(msg)
        else:
            raise serializers.ValidationError({'Error:': ["A user doesn't exist with this email address."]})

        if "rest_auth.registration" in settings.INSTALLED_APPS:
            from allauth.account import app_settings

            if (
                app_settings.EMAIL_VERIFICATION
                == app_settings.EmailVerificationMethod.MANDATORY
            ):
                if user.email is None:
                    msg = {'Error:': ["This account doesn't have an E-mail address!, so that you can't login."]}
                    raise serializers.ValidationError(msg)

        attrs["user"] = user
        return attrs
    
    def create(self, validated_data):
        user = self.validated_data['user']
        token = RefreshToken.for_user(user)
        token = {
            "refresh_token": str(token),
            "access_token": str(token.access_token)
        }
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        user = login(self.request, user)

        return token


class ResendEmailSerializer(serializers.Serializer):
    email = serializers.CharField(required=True)

    def __init__(self, *args, **kwargs):
        super(ResendEmailSerializer, self).__init__(*args, **kwargs)

        self.request = self.context.get("request")
    
    def create(self, validated_data):
        email = self.validated_data.get('email')
        email_adddres = EmailAddress.objects.get(email=email)
        confirmation = EmailConfirmationHMAC(email_adddres)
        key = confirmation.key
        send_register_mail.delay(email_adddres.user.id, key)
        return key

from email.policy import default
import os
from django.contrib.auth import get_user_model, authenticate
from django.conf import settings
from django.contrib.auth.forms import SetPasswordForm
from rest_framework import serializers, exceptions
from phonenumber_field.serializerfields import PhoneNumberField
from rest_auth.registration.serializers import RegisterSerializer
from rest_framework.validators import UniqueValidator 
from django.utils.translation import gettext_lazy as _
from .models import Business, Customer
from . import google_validate
from .social_register import validate_social_user
from main.utils import id_generator

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
                'Must include "username or "email" or "phone number" and "password".'
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
                'Must include either "username" or "email" or "phone number" and "password".'
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
                if user.email is not None:
                    email_address = user.emailaddress_set.get(email=user.email)
                else:
                    raise serializers.ValidationError(
                        _(
                            "This account doesn't have an E-mail address!, so that you can't login."
                        )
                    )
                if not email_address.verified:
                    raise serializers.ValidationError(_("E-mail is not verified."))

        attrs["user"] = user
        return attrs


class CustomRegisterSerializer(RegisterSerializer):
    username = serializers.CharField(required=False, write_only=True)
    first_name = serializers.CharField(required=False, write_only=True)
    last_name = serializers.CharField(required=False, write_only=True)
    email = serializers.EmailField(required=True, write_only=True)
    agreement = serializers.BooleanField(default=False)
    account_type = serializers.CharField(required=True, write_only=True)
    

    def get_cleaned_data_customer(self):
        return {
            "first_name": self.validated_data.get("first_name", ""),
            "last_name": self.validated_data.get("last_name", ""),
            "agreement": self.validated_data.get("agreement", ""),
        }
    
    def get_cleaned_data_business(self):
        return {
            "agreement": self.validated_data.get("agreement", ""),
        }
    
    def validate(self, attrs):
        agreement = attrs['agreement']
        if agreement is not True:
            raise serializers.ValidationError({'Agreement': ['You must agree to our terms & conditions']})
        return attrs

    def create_customer(self, user, validated_data):
        user.first_name = self.validated_data.get("first_name")
        user.last_name = self.validated_data.get("last_name")
        user.email = self.validated_data.get("email")
        user.username = self.validated_data.get("username")
        user.save()

        Customer.objects.create(
            user=user,
            full_name = self.validated_data.get("first_name") + " " + self.validated_data.get("last_name"),
            provider='Email'
        )
    
    def create_business(self, user, validated_data):
        user.email = self.validated_data.get('email')
        user.username = id_generator()
        user.save()

        Business.objects.create(
            user=user, 
            provider='Email'
        )

    def custom_signup(self, request, user):
        if self.validated_data.get('account_type') == 'Bussines':
            self.create_bussines(user, self.get_cleaned_data_customer())
        else:
            self.create_customer(user, self.get_cleaned_data_business())


class UserSerializer(serializers.ModelSerializer):
    address = serializers.ImageField(source="customer.address")
    postcode = serializers.CharField(source="customer.postcode")
    account_type = serializers.CharField(source="customer.account_type")
    phone = PhoneNumberField(source="customer.phone")
    property_type = serializers.CharField(source="customer.property_type")
    no_floors = serializers.CharField(source="customer.no_floors")
    bill_rate = serializers.CharField(source="customer.bill_rate")
    agreement = serializers.BooleanField(source="customer.agreement")
    other = serializers.CharField(source="customer.other")

    class Meta:
        model = get_user_model()
        fields = [
            "id",
            "username",
            "email",
            "password",
            "address",
            "postcode",
            "property_type",
            "no_floors",
            "bill_rate",
            "agreement",
            "other",
        ]

class BussinesUserSerializer(serializers.ModelSerializer):
    address = serializers.ImageField(source="business.address")
    postcode = serializers.CharField(source="business.postcode")
    account_type = serializers.CharField(source="business.account_type")
    phone = PhoneNumberField(source="business.phone")
    property_type = serializers.CharField(source="business.property_type")
    no_floors = serializers.CharField(source="business.no_floors")
    bill_rate = serializers.CharField(source="business.bill_rate")
    company_name = serializers.BooleanField(source="business.company_name")
    other = serializers.CharField(source="business.other")

    class Meta:
        model = get_user_model()
        fields = [
            "id",
            "email",
            "password",
            "address",
            "postcode",
            "property_type",
            "no_floors",
            "bill_rate",
            "other",
            "company_name"
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
    account_type = serializers.CharField(required=True, write_only=True)

    def validate_auth_token(self, auth_token):
        user_data = google_validate.Google.validate(auth_token)
        print("user data: ", user_data)
        try:
            user_data['sub']
        except:
            raise serializers.ValidationError(
                'Invalid TOKEN'
            )

        if user_data['aud'] != os.environ['GOOGLE_CLIENT_ID']:
            raise serializers.ValidationError("User not found")

        email = user_data['email']
        name = user_data['name']
        provider = 'google'

        return validate_social_user(email, name, provider, self.account_type)

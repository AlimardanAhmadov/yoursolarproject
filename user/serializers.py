from django.contrib.auth import get_user_model, authenticate
from django.conf import settings
from django.contrib.auth.forms import SetPasswordForm
from rest_framework import serializers, exceptions
from phonenumber_field.serializerfields import PhoneNumberField
from rest_auth.registration.serializers import RegisterSerializer
from rest_framework.validators import UniqueValidator 
from django.utils.translation import gettext_lazy as _
from .models import Customer

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
    username = serializers.CharField(required=True, write_only=True)
    first_name = serializers.CharField(required=True, write_only=True)
    last_name = serializers.CharField(required=True, write_only=True)
    email = serializers.EmailField(required=True, write_only=True)
    phone = PhoneNumberField(
        required=True,
        write_only=True,
        validators=[
            UniqueValidator(
                queryset=Customer.objects.all(),
                message=_("A user is already registered with this phone number."),
            )
        ],
    )
    other = serializers.CharField(required=False, write_only=True)
    company_name = serializers.CharField(required=False, write_only=True)
    
    extra_kwargs = {
        'company_name': {'required': False},
    }

    def get_cleaned_data_customer(self):
        return {
            "first_name": self.validated_data.get("first_name", ""),
            "last_name": self.validated_data.get("last_name", ""),
            "address": self.validated_data.get("address", ""),
            "postcode": self.validated_data.get("postcode", ""),
            "house_type": self.validated_data.get("house_type", ""),
            "no_floors": self.validated_data.get("no_floors", ""),
            "no_bedrooms": self.validated_data.get("no_bedrooms", ""),
            "bill_rate": self.validated_data.get("bill_rate", ""),
            "agreement": self.validated_data.get("agreement", ""),
            "other": self.validated_data.get("other", ""),
            "phone": self.validated_data.get("phone", ""),
            "account_type": self.validated_data.get("account_type", ""),
            "company_name": self.validated_data.get("company_name", ""),
        }

    def create_customer(self, user, validated_data):
        user.first_name = self.validated_data.get("first_name")
        user.last_name = self.validated_data.get("last_name")
        user.email = self.validated_data.get("email")
        user.username = self.validated_data.get("username")
        user.save()

        if self.get_cleaned_data_customer['account_type'] == 'Bussiness' and self.get_cleaned_data_customer['company_name'] is None:
            raise serializers.ValidationError('Company name is required for bussiness accounts!')

        Customer.objects.create(
            user=user,
            full_name = self.validated_data.get("first_name") + " " + self.validated_data.get("last_name")
        )

    def custom_signup(self, request, user):
        self.create_customer(user, self.get_cleaned_data_customer())


class UserSerializer(serializers.ModelSerializer):
    address = serializers.ImageField(source="customer.address")
    postcode = serializers.CharField(source="customer.postcode")
    account_type = serializers.CharField(source="customer.account_type")
    phone = PhoneNumberField(source="customer.phone")
    house_type = serializers.CharField(source="customer.house_type")
    no_floors = serializers.CharField(source="customer.no_floors")
    no_bedrooms = serializers.CharField(source="customer.no_bedrooms")
    bill_rate = serializers.CharField(source="customer.bill_rate")
    agreement = serializers.BooleanField(source="customer.agreement")
    company_name = serializers.CharField(source="customer.company_name")
    other = serializers.CharField(source="customer.other")

    class Meta:
        model = get_user_model()
        fields = [
            "id",
            "username",
            "email",
            "password",
            "first_name",
            "last_name",
            "address",
            "postcode",
            "house_type",
            "no_floors",
            "no_bedrooms",
            "bill_rate",
            "agreement",
            "company_name",
            "other",
            "account_type"
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
            self.old_password_field_enabled,
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



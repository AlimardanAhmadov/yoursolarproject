import os
from django.db import transaction
from django.contrib.auth import authenticate, get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import serializers

from main.utils import id_generator
from user.models import Business, Customer

User = get_user_model()


def random_username(name):
    username = "".join(name.split(' ')).lower()
    if not User.objects.filter(username=username).exists():
        return username
    else:
        random_username = username + id_generator()
        return random_username(random_username)


def validate_social_user(provider, email, name):
    with transaction.atomic():
        try:
            selected_user = User.objects.filter(email=email)

            if selected_user.exists():

                if provider == selected_user[0].customer.provider:

                    registered_user = authenticate(
                        email=email, password=os.environ['SECRET_PASSWORD'])

                    token = RefreshToken.for_user(registered_user)
                    token = {
                        "refresh_token": str(token),
                        "access_token": str(token.access_token)
                    }
                    return {
                        'username': registered_user.username,
                        'email': registered_user.email,
                        'tokens': token}

                else:
                    transaction.set_rollback(True)
                    raise serializers.ValidationError(
                        detail="We've found an existing Solar Panels account. Please continue to log in with your account email or username below.")

            else:
                args = {
                    'username': random_username(name), 'email': email,
                    'password': os.environ['SECRET_PASSWORD']}

                user = User.objects.create_user(**args)
                user.save()
                if account_type == 'Business':
                    new_business = Business(
                        provider=provider,
                        user=user
                    )
                    new_business.save()
                else:
                    new_customer=Customer(
                        user=user,
                        provider=provider,
                    )
                    new_customer.save()

                logged_user = authenticate(
                    email=email, password=os.environ['SECRET_PASSWORD'])

                token = RefreshToken.for_user(logged_user)
                token = { 
                    "refresh_token": str(token),
                    "access_token": str(token.access_token)
                }
                return {
                    'email': logged_user.email,
                    'username': logged_user.username,
                    'tokens': token
                }

        except:
            transaction.set_rollback(True)
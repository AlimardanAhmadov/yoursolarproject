import os
from django.contrib.auth import authenticate, get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import serializers

from main.utils import id_generator
from user.models import Customer

User = get_user_model()


def random_username(name):
    username = "".join(name.split(' ')).lower()
    if not User.objects.filter(username=username).exists():
        return username
    else:
        random_username = username + id_generator()
        return random_username(random_username)


def validate_social_user(provider, email, name):
    selected_user = User.objects.filter(email=email)

    if selected_user.exists():

        if provider == selected_user[0].customer.auth_provider:

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
            raise serializers.ValidationError(
                detail='Please sign in using' + selected_user[0].auth_provider)

    else:
        args = {
            'username': random_username(name), 'email': email,
            'password': os.environ['SECRET_PASSWORD']}

        user = User.objects.create_user(**args)
        user.customer.provider = provider
        user.save()

        new_customer=Customer(
            user=user,
        )
        new_customer.save()

        new_user = authenticate(
            email=email, password=os.environ['SECRET_PASSWORD'])
        
        #Refresh/generate token on register

        token = RefreshToken.for_user(user)
        token = { 
            "refresh_token": str(token),
            "access_token": str(token.access_token)
        }
        return {
            'email': new_user.email,
            'username': new_user.username,
            'tokens': token
        }


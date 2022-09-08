from django.contrib.auth.backends import AllowAllUsersModelBackend, ModelBackend
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied

User = get_user_model()


class EmailBackend(AllowAllUsersModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get("username")
        try:
            user = User.objects.get(email=username)
        except User.DoesNotExist:
            raise PermissionDenied("This User does't exist.")

        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user


class PasswordlessAuthBackend(ModelBackend):
    def authenticate(self, request, email):
        try:
            user = User.objects.get(email=email)
            return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        User = get_user_model()
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
            
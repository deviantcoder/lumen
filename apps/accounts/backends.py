from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q


User=  get_user_model()


class UsernameOrEmailLoginBackend(ModelBackend):
    """
    Custom authentication backend to allow login with either username or email.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(
                Q(username__iexact=username) | Q(email__iexact=username)
            )

            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None

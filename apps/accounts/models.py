from uuid import uuid4

from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    username = models.CharField(max_length=50, unique=True)

    email = models.EmailField(max_length=200, unique=True)
    account_activated = models.BooleanField(default=False)

    last_activation_email_sent = models.DateTimeField(null=True, blank=True)

    full_name = models.CharField(max_length=100, null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    public_id = models.UUIDField(default=uuid4, unique=True, editable=False)

    class Meta:
        ordering = ('-created',)
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.username

    @property
    def get_full_name(self):
        return self.full_name if self.full_name else self.username

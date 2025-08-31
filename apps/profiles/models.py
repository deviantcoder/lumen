from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator

from utils.images import base_upload_to, ALLOWED_EXTENSIONS


User = get_user_model()


def upload_to(filename, instance):
    return base_upload_to(filename, instance)


class Profile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='profile'
    )

    image = models.ImageField(
        upload_to=upload_to,
        validators=[
            FileExtensionValidator(ALLOWED_EXTENSIONS),
        ]
    )

    bio = models.TextField(max_length=500, null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)
    url = models.URLField(max_length=200, null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'
    
    def __str__(self):
        return f'{self.user.username} (profile)'
    
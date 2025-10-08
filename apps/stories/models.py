import shortuuid

from datetime import timedelta

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator
from django.utils import timezone

from utils.files import (
    base_upload_to, ALLOWED_IMAGE_EXTENSIONS, ALLOWED_VIDEO_EXTENSIONS, validate_file_size
)


User = get_user_model()


def generate_public_id():
    return shortuuid.uuid()


def set_expiry_datetime(hours: int = 24):
    return timezone.now() + timedelta(hours=hours)


def upload_to(instance, filename):
    return base_upload_to(instance, filename, base_dir='stories')


class Story(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='stories')

    media = models.FileField(
        upload_to=upload_to,
        validators=[
            FileExtensionValidator(ALLOWED_IMAGE_EXTENSIONS + ALLOWED_IMAGE_EXTENSIONS),
            validate_file_size
        ]
    )

    created = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default=set_expiry_datetime)

    public_id = models.CharField(max_length=22, unique=True, default=generate_public_id)

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Story'
        verbose_name_plural = 'Stories'

    def __str__(self):
        return f'{self.author.username} (story)'

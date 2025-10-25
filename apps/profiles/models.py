import logging

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator

from utils.files import (
    base_upload_to, ALLOWED_IMAGE_EXTENSIONS, validate_file_size
)


logger = logging.getLogger(__name__)

User = get_user_model()


def upload_to(instance, filename):
    return base_upload_to(instance, filename, base_dir='profiles', id_attr='user.public_id')


class Profile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='profile'
    )

    image = models.ImageField(
        upload_to=upload_to,
        validators=[
            FileExtensionValidator(ALLOWED_IMAGE_EXTENSIONS),
            validate_file_size,
        ],
        null=True, blank=True
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
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    @property
    def image_or_default(self):
        if self.image:
            return self.image.url
        return '/static/img/def.png'
    
    @property
    def username(self):
        return self.user.username


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')

    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Follow'
        verbose_name_plural = 'Follows'
        unique_together = ('user', 'follower')

    def __str__(self):
        return f'{self.follower.username} -> {self.user.username}'

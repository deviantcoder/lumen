import shortuuid

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator

from utils.files import (
    ALLOWED_VIDEO_EXTENSIONS, ALLOWED_IMAGE_EXTENSIONS, base_upload_to
)


User = get_user_model()


def generate_public_id():
    return shortuuid.uuid()


def upload_to(instance, filename):
    return base_upload_to(instance, filename, base_dir='posts')


class Post(models.Model):

    class POST_STATUSES(models.TextChoices):
        ACTIVE = ('active', 'Active')
        HIDDEN = ('hidden', 'Hidden')

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    
    caption = models.TextField(max_length=500, null=True, blank=True)

    status = models.CharField(max_length=10, choices=POST_STATUSES.choices, default=POST_STATUSES.ACTIVE)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    public_id = models.CharField(max_length=22, unique=True, default=generate_public_id)

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'

    def __str__(self):
        return f'{self.author.username}: {self.caption[:20]}'


class PostMedia(models.Model):

    class MEDIA_TYPES(models.TextChoices):
        IMAGE = ('image', 'Image')
        VIDEO = ('video', 'Video')

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='media')

    file = models.FileField(
        upload_to=upload_to,
        validators=[
            FileExtensionValidator(ALLOWED_IMAGE_EXTENSIONS + ALLOWED_VIDEO_EXTENSIONS),
            # file size validator
        ]
    )
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPES.choices, default=MEDIA_TYPES.IMAGE)

    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('post',)
        verbose_name = 'Post Media File'
        verbose_name_plural = 'Post Media Files'

    def __str__(self):
        return f'{self.post} (media)'

    

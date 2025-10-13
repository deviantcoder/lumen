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


def upload_to_factory(base_dir: str):
    def upload_to(instance, filename):
        return base_upload_to(instance, filename, base_dir=base_dir)
    return upload_to


story_upload_to = upload_to_factory(base_dir='stories')
collection_upload_to = upload_to_factory(base_dir='collections')


class Story(models.Model):

    class STORY_TYPES(models.TextChoices):
        IMAGE = ('image', 'Image')
        VIDEO = ('video', 'Video')

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='stories')

    media = models.FileField(
        upload_to=story_upload_to,
        validators=[
            FileExtensionValidator(ALLOWED_IMAGE_EXTENSIONS + ALLOWED_VIDEO_EXTENSIONS),
            validate_file_size
        ]
    )

    story_type = models.CharField(
        max_length=5, choices=STORY_TYPES.choices, default=STORY_TYPES.IMAGE
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



class Collection(models.Model):
    
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='collections')

    name = models.CharField(max_length=200)
    stories = models.ManyToManyField(Story, related_name='collections', blank=True)
    
    image = models.ImageField(
        upload_to=collection_upload_to,
        validators=[
            FileExtensionValidator(ALLOWED_IMAGE_EXTENSIONS),
            validate_file_size
        ],
        null=True, blank=True
    )
    
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    public_id = models.CharField(max_length=22, unique=True, default=generate_public_id)

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Collection'
        verbose_name_plural = 'Collections'

    def __str__(self):
        return f'{self.name}: {self.owner}'
    
    @property
    def image_or_default(self):
        if self.image:
            return self.image.url
        if self.stories.exists():
            return self.stories.first().media.url
        return '/static/img/def_collection.jpg'

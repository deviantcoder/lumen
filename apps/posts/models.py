import shortuuid

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator
from django.utils.text import slugify
from django.db import IntegrityError, transaction

from utils.files import (
    ALLOWED_VIDEO_EXTENSIONS, ALLOWED_IMAGE_EXTENSIONS, base_upload_to, validate_file_size
)

from mptt.models import MPTTModel, TreeForeignKey


User = get_user_model()


def generate_public_id():
    return shortuuid.uuid()


def upload_to(instance, filename):
    return base_upload_to(instance, filename, base_dir='posts', id_attr='post.public_id')


class Post(models.Model):

    class POST_STATUS(models.TextChoices):
        ACTIVE = ('active', 'Active')
        HIDDEN = ('hidden', 'Hidden')

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    
    caption = models.TextField(max_length=500, null=True, blank=True)
    tags = models.ManyToManyField('Tag', related_name='tags')
    status = models.CharField(max_length=10, choices=POST_STATUS.choices, default=POST_STATUS.ACTIVE)

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
            validate_file_size,
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


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name.lower())
            self.slug = base_slug

        for _ in range(5):
            try:
                with transaction.atomic():
                    super().save(*args, **kwargs)
                return
            except IntegrityError:
                self.slug = f'{base_slug}-{shortuuid.uuid()[:8]}'
        
        raise IntegrityError(f'Could not generate unique slug for tag: {self.name}')


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='liked_posts')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')

    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created',)
        unique_together = ('post', 'user')
        verbose_name = 'Like'
        verbose_name_plural = 'Likes'

    def __str__(self):
        return f'{self.user}: {self.post.caption[:20]}'


class Save(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_posts')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='saves')

    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created',)
        unique_together = ('user', 'post')
        verbose_name = 'Save'
        verbose_name_plural = 'Saves'

    def __str__(self):
        return f'{self.user}: {self.post.caption[:20]}'


class Comment(MPTTModel): 
    
    class COMMENT_STATUS(models.TextChoices):
        ACTIVE = ('active', 'Active')
        HIDDEN = ('hidden', 'Hidden')

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='comments')

    body = models.TextField(blank=True)

    created = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=COMMENT_STATUS.choices, default=COMMENT_STATUS.ACTIVE)

    class MPTTMeta:
        order_insertion_by = ['post']

    def __str__(self):
        return f'{self.user.username} - {self.post.caption[:20]} (comment)'

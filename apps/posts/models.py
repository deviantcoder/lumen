import shortuuid

from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


def generate_public_id():
    return shortuuid.uuid()


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

from uuid import uuid4

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone


User = get_user_model()


class Chat(models.Model):

    members = models.ManyToManyField(User, related_name='chats')

    online_members = models.ManyToManyField(User, related_name='online', blank=True)

    created = models.DateTimeField(auto_now_add=True)
    id = models.UUIDField(default=uuid4, unique=True, editable=False, primary_key=True)

    class Meta:
        verbose_name = 'Chat'
        verbose_name_plural = 'Chats'
        ordering = ('-created',)

    def __str__(self):
        return f'Chat: {', '.join([user.username for user in self.members.all()])}'
    
    def get_other_user(self, current_user):
        return self.members.exclude(pk=current_user.pk).first()


class Message(models.Model):

    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages_sent')
    
    content = models.TextField()

    is_read = models.BooleanField(default=False)
    
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
        ordering = ('-created',)

    def __str__(self):
        return f'{self.sender.username}: {self.content[:20]}'

    @property
    def time_sent(self):
        return timezone.localtime(self.created).strftime('%H:%M')

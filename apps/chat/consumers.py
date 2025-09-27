import json

from asgiref.sync import sync_to_async

from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from .models import Chat, Message


class ChatConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):

        self.user = self.scope['user']
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']

        self.chat = await self.get_chat(self.chat_id)

        await self.channel_layer.group_add(
            str(self.chat_id), self.channel_name
        )

        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            str(self.chat_id), self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        content = text_data_json.get('content')

        message = await self.create_message(
            self.chat, self.user, content
        )

        event = {
            'type': 'message_handler',
            'message_id': message.pk,
        }

        await self.channel_layer.group_send(
            str(self.chat_id), event
        )

    async def message_handler(self, event):
        message_id = event.get('message_id')

        message = await self.get_message(message_id)

        html = await self.render_message_partial(message, self.user)

        await self.send(text_data=html)

    # -----------

    @database_sync_to_async
    def get_chat(self, chat_id):
        return get_object_or_404(Chat, id=chat_id)
    
    
    @database_sync_to_async
    def create_message(self, chat, sender, content):
        return Message.objects.create(
            chat=chat, sender=sender, content=content
        )


    @database_sync_to_async
    def get_message(self, message_id):
        return get_object_or_404(Message, pk=message_id)


    @sync_to_async
    def render_message_partial(self, message, user):
        context = {
            'message': message,
            'user': user,
        }
        return render_to_string('chat/partials/message_p.html', context)
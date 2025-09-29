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
        self.chat_id = str(self.scope['url_route']['kwargs']['chat_id'])

        self.chat = await self.get_chat(self.chat_id)

        await self.channel_layer.group_add(
            self.chat_id, self.channel_name
        )

        await self.add_user_to_online(self.chat, self.user)
        await self.update_online_status()
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.chat_id, self.channel_name
        )

        await self.remove_user_from_online(self.chat, self.user)
        await self.update_online_status()

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
            self.chat_id, event
        )

    async def message_handler(self, event):
        message_id = event.get('message_id')
        message = await self.get_message(message_id)

        html = await self.render_message_partial(message, self.user)

        await self.send(text_data=html)

    async def update_online_status(self):
        online_members = await self.get_online_members(self.chat)

        event = {
            'type': 'online_status_handler',
            'online_members': online_members,
        }

        await self.channel_layer.group_send(
            self.chat_id, event
        )

    async def online_status_handler(self, event):
        online_members = event.get('online_members')

        html = await self.render_online_status_partial(
            self.chat, online_members, self.user
        )

        await self.send(text_data=html)

    # ----------- DB helpers -----------

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

    @database_sync_to_async
    def get_online_members(self, chat):
        return list(chat.online_members.values_list("id", flat=True))

    @database_sync_to_async
    def add_user_to_online(self, chat, user):
        if not chat.online_members.filter(pk=user.pk).exists():
            chat.online_members.add(user)

    @database_sync_to_async
    def remove_user_from_online(self, chat, user):
        if chat.online_members.filter(pk=user.pk).exists():
            chat.online_members.remove(user)

    # ----------- Rendering -----------

    @sync_to_async
    def render_message_partial(self, message, user):
        context = {
            'message': message,
            'user': user,
        }

        return render_to_string('chat/partials/message_p.html', context)

    @sync_to_async
    def render_online_status_partial(self, chat, online_members, current_user):
        other_user = chat.members.exclude(pk=current_user.pk).first()
        is_online = other_user.id in online_members if other_user else False

        context = {
            'other_user': other_user,
            'is_online': is_online,
        }

        return render_to_string('chat/partials/online_status.html', context)

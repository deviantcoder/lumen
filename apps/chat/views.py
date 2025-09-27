from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

from .forms import MessageForm
from .models import Chat


User = get_user_model()


@login_required
def inbox(request):
    user_chats = request.user.chats.all()

    chats = [
        {'chat': chat, 'other_user': chat.get_other_user(request.user)}
        for chat in user_chats
    ]
    
    context = {
        'chats': chats,
    }

    return render(request, 'chat/inbox.html', context)


@login_required
def chat(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)

    form = MessageForm()

    current_user = request.user
    other_user = chat.get_other_user(current_user)

    chat_messages = chat.messages.all()
    
    context = {
        'chat': chat,
        'form': form,
        'other_user': other_user,
        'chat_messages': chat_messages,
    }
    
    return render(request, 'chat/chat.html', context)


@login_required
def start_chat(request, username):

    current_user = request.user
    other_user = get_object_or_404(User, username=username)

    chat = current_user.chats.distinct().filter(members=other_user).first()

    if not chat:
        chat = Chat.objects.create()
        chat.members.add(current_user, other_user)

    return redirect('chat:chat', chat.id)

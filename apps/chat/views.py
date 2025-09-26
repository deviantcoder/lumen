from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def inbox(request):
    context = {}
    return render(request, 'chat/inbox.html', context)


@login_required
def chat(request):
    context = {}
    return render(request, 'chat/chat.html', context)

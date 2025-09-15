from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from django.contrib.auth import get_user_model


User = get_user_model()


@login_required
def profile(request, username: str):

    if username == request.user.username:
        user = request.user
    user = get_object_or_404(User, username=username)

    context = {
        'profile': user.profile,
        'posts': user.posts.all(),
    }

    return render(request, 'profiles/profile.html', context)

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from django.contrib.auth import get_user_model

from apps.posts.models import Post


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


@login_required
def get_user_posts(request, username):
    user = get_object_or_404(User, username=username)

    posts = user.posts.filter(status=Post.POST_STATUSES.ACTIVE)

    if 'saved' in request.GET:
        saved_posts_pks = user.saved_posts.values_list('post', flat=True)
        posts = Post.objects.filter(
            pk__in=saved_posts_pks,
            status=Post.POST_STATUSES.ACTIVE
        )

    context = {
        'posts': posts,
    }

    return render(request, 'profiles/partials/user_posts_list.html', context)

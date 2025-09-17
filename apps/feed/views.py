from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Exists, OuterRef

from apps.posts.models import Post, Like, Save


@login_required
def feed(request):
    posts = Post.objects.all().annotate(
        liked=Exists(
            Like.objects.filter(user=request.user, post=OuterRef('pk'))
        ),
        saved=Exists(
            Save.objects.filter(user=request.user, post=OuterRef('pk'))
        )
    )

    context = {
        'posts': posts,
    }

    return render(request, 'feed/feed.html', context)

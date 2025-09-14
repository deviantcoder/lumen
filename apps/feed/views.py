from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from apps.posts.models import Post


@login_required
def feed(request):
    posts = Post.objects.all()

    context = {
        'posts': posts,
    }

    return render(request, 'feed/feed.html', context)

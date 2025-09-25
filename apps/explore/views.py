from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count

from apps.posts.models import Post


@login_required
def explore(request):
    posts = (
        Post.objects.all()
        .select_related('author', 'author__profile')
        .prefetch_related('media')
        .annotate(
            likes_count=Count('likes'),
            comments_count=Count('comments'),
        )
    )

    context = {
        'posts': posts,
    }

    return render(request, 'explore/explore.html', context)

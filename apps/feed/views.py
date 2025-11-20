from datetime import timedelta

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.conf import settings
from django.db.models import (
    Exists, OuterRef,
    Count, Case, When,
    IntegerField, F, Q
)
from django.core.paginator import (
    Paginator,
    PageNotAnInteger,
    EmptyPage
)

from apps.posts.models import (
    Post, Like, Save, PostMedia
)


def get_feed_queryset(user):
    return (
        Post.objects.filter(
            Q(author=user) | Q(author__followers__follower=user)
        )
        .select_related('author', 'author__profile')
        .prefetch_related(
            'media', 'tags', 'likes', 'comments'
        )
        .annotate(
            liked=Exists(Like.objects.filter(user=user, post=OuterRef('pk'))),
            saved=Exists(Save.objects.filter(user=user, post=OuterRef('pk'))),

            likes_count=Count('likes', distinct=True),
            comments_count=Count('comments', distinct=True),
            
            priority_score=Case(
                When(author=user, then=100),
                default=10,
                output_field=IntegerField()
            ),
            time_score=Case(
                When(created__gte=timezone.now() - timedelta(hours=24), then=20),
                When(created__gte=timezone.now() - timedelta(days=7), then=10),
                When(created__gte=timezone.now() - timedelta(days=30), then=5),
                default=1,
                output_field=IntegerField()
            ),
        )
        .annotate(
            final_score=F('priority_score') + F('time_score') + F('likes_count') + F('comments_count')
        )
        .order_by('-final_score', '-created')
    )


@login_required
def feed(request):
    posts = get_feed_queryset(user=request.user)

    paginator = Paginator(
        posts, getattr(settings, 'PER_PAGE', 5)
    )
    page = request.GET.get('page', 1)

    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    if request.headers.get('HX-Request'):
        template_name = 'posts/includes/posts_list.html'
    else:
        template_name = 'feed/feed.html'

    context = {
        'posts': posts,
    }

    return render(request, template_name, context)

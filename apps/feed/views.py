from datetime import timedelta

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import (
    Exists, OuterRef, Prefetch, Count, Case, When, IntegerField, F, Q
)
from django.utils import timezone

from apps.posts.models import (
    Post, Like, Save
)


@login_required
def feed(request):
    user = request.user
    posts = (
        Post.objects.filter(
            Q(author=user) | Q(author__followers__follower=user)
        )
        .annotate(
            liked=Exists(Like.objects.filter(user=user, post=OuterRef('pk'))),
            saved=Exists(Save.objects.filter(user=user, post=OuterRef('pk'))),

            likes_count=Count('likes'),
            comments_count=Count('comments'),

            priority_score=Case(
                When(author=user, then=100),
                # When(author__id__in=friends_ids, then=50) # <<<<< Change when friend system is done
                default=10,
                output_field=IntegerField()
            ),

            time_score=Case(
                When(
                    created__gte=timezone.now() - timedelta(hours=24),
                    then=20
                ),
                When(
                    created__gte=timezone.now() - timedelta(days=7),
                    then=10
                ),
                When(
                    created__gte=timezone.now() - timedelta(days=30),
                    then=5
                ),
                default=1,
                output_field=IntegerField()
            )
        )
        .annotate(
            final_score=F('priority_score') + F('time_score') + F('likes_count') + F('comments_count')
        )
        .order_by('-final_score', '-created')
        .select_related('author', 'author__profile')
        .prefetch_related(
            Prefetch('media'),
            Prefetch('tags'),
            'likes',
            'comments',
        )
    )

    context = {
        'posts': posts,
    }

    return render(request, 'feed/feed.html', context)

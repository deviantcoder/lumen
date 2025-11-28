from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, F
from django.core.paginator import (
    Paginator,
    PageNotAnInteger,
    EmptyPage
)
from django.urls import reverse

from apps.posts.models import Post


@login_required
def explore(request):
    user = request.user
    following_ids = user.following.values_list('user__id', flat=True)

    posts = (
        Post.objects.all()
        .exclude(author__id__in=following_ids)
        .exclude(author__id=user.id)
        .select_related('author', 'author__profile')
        .prefetch_related('media')
        .annotate(
            likes_count=Count('likes', distinct=True),
            comments_count=Count('comments', distinct=True),

            foaf_score = Count(
                'author__followers',
                filter=Q(author__followers__follower__in=following_ids),
                distinct=True
            ),

            liked_by_following_score = Count(
                'likes',
                filter=Q(likes__user__id__in=following_ids),
                distinct=True
            ),

            explore_score = (
                5 * F('likes_count') +
                3 * F('comments_count') +
                10 * F('liked_by_following_score') +
                6 * F('foaf_score')
            )
        )
        .order_by(
            '-explore_score',
            '-created'
        )
    )

    paginator = Paginator(
        posts, per_page=6
    )
    page = request.GET.get('page', 1)

    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    if request.htmx:
        template_name = 'posts/partials/posts_grid.html'
    else:
        template_name = 'discovery/explore/explore.html'

    context = {
        'posts': posts,
        'load_url': reverse('discovery:explore')
    }

    return render(request, template_name, context)

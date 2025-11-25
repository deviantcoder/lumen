from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.urls import reverse

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
        .order_by('-created')
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
from urllib.parse import urlencode

from django.shortcuts import render
from django.db.models import Q, Count
from django.http import Http404
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.urls import reverse

from apps.discovery.documents.posts import PostDocument
from apps.discovery.documents.profiles import ProfileDocument

from apps.posts.filters import PostFilter


def search(request):
    """
    Search for posts and profiles based on a query string
    using Elasticsearch.
    """

    search_query = request.GET.get('query', '')

    if not search_query:
        return render(
            request,
            'discovery/search/search_results.html',
            {
                'posts': [],
                'profiles': [],
                'search_query': '',
            }
        )

    es_posts = (
        PostDocument.search()
        .query(
            'multi_match',
            query=search_query,
            fields=[
                'caption^3',
                'tag_names',
                'author__username',
            ],
            fuzziness='AUTO'
        )
        .extra(size=1000)
        .to_queryset()
        .select_related(
            'author', 'author__profile'
        )
        .prefetch_related('media')
        .annotate(
            likes_count=Count('likes'),
            comments_count=Count('comments')
        )
        .order_by('-created')
    )

    es_profiles = (
        ProfileDocument.search()
        .query(
            'multi_match',
            query=search_query,
            fields=[
                'username^3',
                'full_name^2',
                'bio',
            ],
            fuzziness='AUTO'
        )
        .to_queryset()
        .select_related('user')
    )

    posts_filter = PostFilter(
        request.GET,
        queryset=es_posts
    )

    paginator = Paginator(
        posts_filter.qs, per_page=6
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
        template_name = 'discovery/search/search_results.html'

    filter_url_params = {
        'query': search_query,
        'page': page,
    }

    context = {
        'posts': posts,
        'profiles': es_profiles,
        'search_query': search_query,
        'load_url': reverse('discovery:search'),
        'filter': posts_filter,
        'filter_url': f'{reverse('discovery:search')}?{urlencode(filter_url_params)}',
    }

    return render(request, template_name, context)

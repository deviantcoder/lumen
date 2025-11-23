from django.shortcuts import render, redirect
from django.db.models import Q, Count
from django.http import Http404

from elastic_transport import ConnectionError

from .documents.posts import PostDocument

from apps.profiles.models import Profile


def search(request):
    search_query = request.GET.get('query', '')

    if not search_query:
        return render(
            request,
            'search/search_results.html',
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
        .to_queryset()
        .select_related(
            'author', 'author__profile'
        )
        .prefetch_related('media')
        .annotate(
            likes_count=Count('likes'),
            comments_count=Count('comments')
        )
    )

    profiles = (
        Profile.objects.filter(
            Q(user__username__icontains=search_query) |
            Q(user__full_name__icontains=search_query)
        )
        .select_related('user')
        .distinct()
    )

    context = {
        'posts': es_posts,
        'profiles': profiles,
        'search_query': search_query,
    }

    return render(request, 'search/search_results.html', context)

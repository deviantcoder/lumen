from django.shortcuts import render, redirect
from django.db.models import Q, Count

from apps.posts.models import Post, Tag
from apps.profiles.models import Profile


def search(request):
    search_query = request.GET.get('query', '')

    tags = Tag.objects.filter(name__icontains=search_query)

    posts = (
        Post.objects.filter(
            Q(caption__icontains=search_query) |
            Q(author__username__icontains=search_query) |
            Q(author__full_name__icontains=search_query) |
            Q(tags__in=tags)
        )
        .select_related('author', 'author__profile')
        .prefetch_related('media')
        .annotate(
            likes_count=Count('likes'),
            comments_count=Count('comments')
        )
        .distinct()
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
        'posts': posts,
        'search_query': search_query,
        'profiles': profiles,
    }

    return render(request, 'search/search_results.html', context)

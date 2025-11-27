from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.http import HttpResponseForbidden
from django.views.decorators.http import require_http_methods
from django.db.models import Count, Q
from django.core.cache import cache
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.urls import reverse
from django.db.models import QuerySet

from apps.posts.models import Post

from .forms import URLForm, BioForm
from .models import Follow, Profile


User = get_user_model()


# ---------- PROFILES ----------


@login_required
def profile(request, username: str):
    user = get_object_or_404(User, username=username)

    is_following = None

    if user != request.user:
        is_following = Follow.objects.filter(
            user=user, follower=request.user
        ).exists()

    posts_count = cache.get(f'user:{user.pk}:posts_count')
    if posts_count is None:
        posts_count = user.posts.filter(status=Post.POST_STATUS.ACTIVE).count()
        cache.set(
            f'user:{user.pk}:posts_count', posts_count, timeout=60 * 15
        )

    following_count = cache.get(f'user:{user.pk}:following_count')
    if following_count is None:
        following_count = Follow.objects.filter(follower=user).count()
        cache.set(
            f'user:{user.pk}:following_count', following_count, timeout=60 * 15
        )

    followers_count = cache.get(f'user:{user.pk}:followers_count')
    if followers_count is None:
        followers_count = Follow.objects.filter(user=user).count()
        cache.set(
            f'user:{user.pk}:followers_count', followers_count, timeout=60 * 15
        )

    context = {
        'profile': user.profile,
        'is_following': is_following,
        'posts_count': posts_count,
        'followers_count': followers_count,
        'following_count': following_count,
    }

    return render(request, 'profiles/profile.html', context)


# ---------- EDITING ----------


@login_required
def edit_profile(request):
    profile = request.user.profile

    url_form = URLForm(instance=profile)
    bio_form = BioForm(instance=profile)

    if request.method == 'POST':
        if 'update_image' in request.POST:
            new_image = request.FILES.get('image')
            if new_image:
                profile.image = new_image
                profile.save(update_fields=['image'])
        
        if 'update_url' in request.POST:
            form = URLForm(request.POST, instance=profile)
            if form.is_valid():
                form.save()
        
        if 'update_bio' in request.POST:
            form = BioForm(request.POST, instance=profile)
            if form.is_valid():
                form.save()
        
        return redirect('profiles:edit_profile')

    context = {
        'profile': profile,
        'url_form': url_form,
        'bio_form': bio_form,
    }

    return render(request, 'profiles/edit_profile.html', context)


# ---------- INTERACTIONS ----------


@require_http_methods(['POST'])
@login_required
def toggle_follow(request, username):
    if request.method == 'POST':
        target_user = get_object_or_404(User, username=username)

        if request.user == target_user:
            return HttpResponseForbidden('You cannot follow yourself')

        follow, created = Follow.objects.get_or_create(user=target_user, follower=request.user)

        if not created:
            follow.delete()
            is_following = False
        else:
            is_following = True

        if request.htmx:
            context = {
                'target_user': target_user,
                'is_following': is_following,
            }

            return render(request, 'profiles/partials/follow_button.html', context)

        return redirect(request.META.get('HTTP_REFERER') or '/')


@login_required
def get_user_posts(request, username):
    user = get_object_or_404(User, username=username)
    posts = []

    if not 'saved' in request.GET:
        posts = (
            user.posts.filter(
                status=Post.POST_STATUS.ACTIVE
            )
            .order_by('-created')
            .annotate(
                likes_count=Count('likes'),
                comments_count=Count('comments'),
            )
            .select_related('author', 'author__profile')
            .prefetch_related('media')
        )
    
    if 'saved' in request.GET and user == request.user:
        saved_posts_pks = user.saved_posts.values_list('post', flat=True)
        posts = (
            Post.objects.filter(
                pk__in=saved_posts_pks,
                status=Post.POST_STATUS.ACTIVE
            )
            .annotate(
                likes_count=Count('likes'),
                comments_count=Count('comments'),
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

    context = {
        'posts': posts,
        'load_url': reverse(
            'profiles:get_user_posts',
            kwargs={
                'username': username,
            }
        )
    }

    return render(request, 'posts/partials/posts_grid.html', context)


@login_required
def get_followers(request, username):
    user = get_object_or_404(User, username=username)
    followers_ids = user.followers.values_list('follower__pk', flat=True)

    followers = User.objects.filter(pk__in=followers_ids)

    context = {
        'followers': followers,
    }

    return render(request, 'profiles/partials/followers.html', context)


@login_required
def get_following(request, username):
    user = get_object_or_404(User, username=username)
    following_ids = user.following.values_list('user__pk', flat=True)

    following = User.objects.filter(pk__in=following_ids)

    context = {
        'following': following,
    }

    return render(request, 'profiles/partials/following.html', context)


@login_required
def suggestions_list(request):
    user = request.user
    limit = 10

    following_ids = user.following.values_list('user__id', flat=True)
    
    suggestions = (
        Profile.objects.filter(
            user__followers__follower__in=following_ids
        )
        .exclude(
            user=user
        )
        .exclude(
            user__id__in=following_ids
        )
        .annotate(
            mutuals_count=Count(
                'user__followers',
                filter=Q(user__followers__follower__in=following_ids),
                distinct=True
            )
        )
        .select_related('user')
        .order_by(
            '-mutuals_count', '-user__created'
        )[:limit]
    )

    context = {
        'suggestions': suggestions,
    }

    return render(request, 'profiles/partials/suggestions_list.html', context)

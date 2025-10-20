from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.http import HttpResponseForbidden
from django.views.decorators.http import require_http_methods
from django.db.models import Count

from apps.posts.models import Post

from .forms import URLForm, BioForm
from .models import Follow


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

    following_count = Follow.objects.filter(follower=user).count()
    followers_count = Follow.objects.filter(user=user).count()

    context = {
        'profile': user.profile,
        'posts': user.posts.all(),
        'is_following': is_following,
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

    context = {
        'profile': profile,
        'url_form': url_form,
        'bio_form': bio_form,
    }

    return render(request, 'profiles/edit_profile.html', context)


@require_http_methods(['POST'])
@login_required
def update_profile_image(request):
    profile = request.user.profile

    if request.method == 'POST':
        new_image = request.FILES.get('image')

        if new_image:
            profile.image = new_image
            profile.save(update_fields=['image'])

            if request.htmx:
                pass
            return redirect('profiles:edit_profile')


@require_http_methods(['POST'])
@login_required
def update_profile_url(request):
    profile = request.user.profile

    if request.method == 'POST':
        form = URLForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            if request.htmx:
                pass
            return redirect('profiles:edit_profile')


@require_http_methods(['POST'])
@login_required
def update_profile_bio(request):
    profile = request.user.profile

    if request.method == 'POST':
        form = BioForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            if request.htmx:
                pass
            return redirect('profiles:edit_profile')


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

        context = {
            'target_user': target_user,
            'is_following': is_following,
        }

        return render(request, 'profiles/partials/follow_button.html', context)
    

@login_required
def get_user_posts(request, username):
    user = get_object_or_404(User, username=username)

    posts = (
        user.posts.filter(
            status=Post.POST_STATUS.ACTIVE
        )
        .order_by('-created')
        .annotate(
            likes_count=Count('likes'),
            comments_count=Count('comments'),
        )
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

    context = {
        'posts': posts,
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

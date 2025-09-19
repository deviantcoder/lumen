from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from django.contrib.auth import get_user_model

from apps.posts.models import Post

from .forms import URLForm, BioForm


User = get_user_model()


@login_required
def profile(request, username: str):

    if username == request.user.username:
        user = request.user
    user = get_object_or_404(User, username=username)

    context = {
        'profile': user.profile,
        'posts': user.posts.all(),
    }

    return render(request, 'profiles/profile.html', context)


@login_required
def get_user_posts(request, username):
    user = get_object_or_404(User, username=username)

    posts = user.posts.filter(status=Post.POST_STATUSES.ACTIVE)
    
    if 'saved' in request.GET and user == request.user:
        saved_posts_pks = user.saved_posts.values_list('post', flat=True)
        posts = Post.objects.filter(
            pk__in=saved_posts_pks,
            status=Post.POST_STATUSES.ACTIVE
        )

    context = {
        'posts': posts,
    }

    return render(request, 'profiles/partials/user_posts_list.html', context)


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

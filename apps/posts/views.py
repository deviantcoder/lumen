from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import PostForm
from .models import PostMedia, Tag, Post, Like, Save


@login_required
def create_post(request):
    form = PostForm()

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()

            files = request.FILES.getlist('files')

            if files:
                for file in files:
                    PostMedia.objects.create(
                        post=post,
                        file=file,
                    )
            
            tags = request.POST.get('tags', '')

            if tags:
                tags_list = [tag.strip().lower() for tag in tags.split('#') if tag.strip()]
                for tag in set(tags_list):
                    tag_obj, _ = Tag.objects.get_or_create(name=tag.lower())
                    post.tags.add(tag_obj)

            messages.success(request, 'Post created!')

            return redirect('/')

    context = {
        'form': form,
    }

    return render(request, 'posts/post_form.html', context)


@login_required
def toggle_like(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    like, created = Like.objects.get_or_create(user=request.user, post=post)

    if not created:
        like.delete()
        messages.success(request, 'Unliked the post.')
    else:
        messages.success(request, 'Liked the post.')

    return redirect(request.META.get('HTTP_REFERER'), 'feed:feed')


@login_required
def toggle_save(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    save, created = Save.objects.get_or_create(user=request.user, post=post)

    if not created:
        save.delete()
        messages.success(request, 'Unsaved the post.')
    else:
        messages.success(request, 'Saved the post.')

    return redirect(request.META.get('HTTP_REFERER'), 'feed:feed')

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Exists, OuterRef
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse

from .forms import PostForm, CommentForm, EditPostForm
from .models import Post, Like, Save, Comment

from apps.profiles.models import Follow
from apps.chat.models import Message, Chat


User = get_user_model()


# ---------- POSTS ----------


@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            form.save(author=request.user)
            return redirect('/')
    else:
        form = PostForm()

    return render(request, 'posts/post_form.html', {'form': form})


@login_required
def post_preview(request, post_id):
    qs = Post.objects.annotate(
        liked=Exists(
            Like.objects.filter(user=request.user, post=OuterRef('pk'))
        ),
        saved=Exists(
            Save.objects.filter(user=request.user, post=OuterRef('pk'))
        )
    )

    post = get_object_or_404(qs, pk=post_id)

    comment_form = CommentForm()

    context = {
        'post': post,
        'comment_form': comment_form,
    }

    return render(request, 'posts/partials/post_preview.html', context)


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    if request.user != post.author:
        return redirect('/')

    tag_names = list(post.tags.all().values_list('name', flat=True))
    tags = ' '.join(f'#{name}' for name in tag_names) if tag_names else ''

    if request.method == 'POST':
        form = EditPostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect(request.META.get('HTTP_REFERER') or '/')
    else:
        form = EditPostForm(tags_=tags, instance=post)

    context = {
        'post': post,
        'form': form, 
    }

    return render(request, 'posts/partials/edit_post.html', context)


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    if request.user != post.author:
        return redirect('/')

    if request.method == 'POST':
        post.delete()
        return redirect(request.META.get('HTTP_REFERER') or '')

    context = {
        'post': post,
    }

    return render(request, 'posts/partials/delete_post.html', context)


# ---------- INTERACTIONS ----------


@require_http_methods(['POST'])
@login_required
def toggle_like(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, pk=post_id)
        like, created = Like.objects.get_or_create(user=request.user, post=post)

        if not created:
            like.delete()
            post.liked = False
        else:
            post.liked = True

        return render(request, 'posts/partials/like_button.html', {'post': post})


@require_http_methods(['POST'])
@login_required
def toggle_save(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, pk=post_id)
        save, created = Save.objects.get_or_create(user=request.user, post=post)

        if not created:
            save.delete()
            post.saved = False
        else:
            post.saved = True

        return render(request, 'posts/partials/save_button.html', {'post': post})


# ---------- COMMENTS ----------


@require_http_methods(['POST'])
@login_required
def add_comment(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, pk=post_id)
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)

            comment.post = post
            comment.author = request.user

            comment.save()

            return render(request, 'posts/partials/comment.html', {'node': comment})


@login_required
def reply_form(request, post_id, comment_id):
    parent_comment = get_object_or_404(Comment, pk=comment_id)
    form = CommentForm(initial={'parent': parent_comment.pk})

    context = {
        'form': form,
        'post': parent_comment.post,
    }

    return render(request, 'posts/partials/reply_form.html', context)


# ---------- SHARING ----------


@login_required
def share_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    mutuals = User.objects.annotate(
        followed_=Exists(
            Follow.objects.filter(follower=request.user, user=OuterRef('pk'))
        ),
    ).filter(
        followed_=True,
    ).select_related('profile')

    context = {
        'mutuals': mutuals,
        'post': post,
    }

    return render(request, 'posts/partials/share.html', context)


@require_http_methods(['POST'])
@login_required
def send_post_to_chat(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, pk=post_id)
        usernames = request.POST.get('recipients', '').split(',')

        recipients = User.objects.filter(username__in=usernames)

        for user in recipients:
            chat = Chat.objects.filter(members=request.user).filter(members=user).first()

            if not chat:
                chat = Chat.objects.create()
                chat.members.add(request.user, user)

            Message.objects.create(
                message_type=Message.MESSAGE_TYPES.POST,
                chat=chat,
                sender=request.user,
                post=post
            )

        response = HttpResponse(status=204)
        response['HX-Trigger'] = 'close'

        return response

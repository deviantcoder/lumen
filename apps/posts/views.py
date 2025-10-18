from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Exists, OuterRef
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse

from .forms import PostForm, CommentForm
from .models import PostMedia, Tag, Post, Like, Save, Comment

from apps.profiles.models import Follow
from apps.chat.models import Message, Chat


User = get_user_model()


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
def reply_form(request, post_id, comment_id):
    parent_comment = get_object_or_404(Comment, pk=comment_id)
    form = CommentForm(initial={'parent': parent_comment.pk})

    context = {
        'form': form,
        'post': parent_comment.post,
    }

    return render(request, 'posts/partials/reply_form.html', context)


@require_http_methods(['POST'])
@login_required
def add_comment(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, pk=post_id)
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)

            comment.post = post
            comment.user = request.user

            comment.save()

            return render(request, 'posts/partials/comment.html', {'node': comment})


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

        # return render(request, 'posts/partials/share_success.html')

        response = HttpResponse(status=204)
        response['HX-Trigger'] = 'close'

        return response

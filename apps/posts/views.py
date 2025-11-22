from datetime import timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import (
    Exists, OuterRef,
    Count, Case, When,
    Q, IntegerField, F
)
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse, Http404
from django.conf import settings
from django.utils import timezone
from django.core.paginator import (
    Paginator,
    PageNotAnInteger,
    EmptyPage
)

from .forms import PostForm, CommentForm, EditPostForm
from .models import Post, Like, Save, Comment
from .filters import PostFilter

from apps.profiles.models import Follow
from apps.chat.models import Message, Chat


User = get_user_model()


# ---------- FEED ----------


def get_feed_queryset(user):
    return (
        Post.objects.filter(
            Q(author=user) | Q(author__followers__follower=user)
        )
        .select_related('author', 'author__profile')
        .prefetch_related(
            'media', 'tags', 'likes', 'comments'
        )
        .annotate(
            liked=Exists(Like.objects.filter(user=user, post=OuterRef('pk'))),
            saved=Exists(Save.objects.filter(user=user, post=OuterRef('pk'))),

            likes_count=Count('likes', distinct=True),
            comments_count=Count('comments', distinct=True),
            
            priority_score=Case(
                When(author=user, then=100),
                default=10,
                output_field=IntegerField()
            ),
            time_score=Case(
                When(created__gte=timezone.now() - timedelta(hours=24), then=20),
                When(created__gte=timezone.now() - timedelta(days=7), then=10),
                When(created__gte=timezone.now() - timedelta(days=30), then=5),
                default=1,
                output_field=IntegerField()
            ),
        )
        .annotate(
            final_score=F('priority_score') + F('time_score') + F('likes_count') + F('comments_count')
        )
        .order_by('-final_score', '-created')
    )


@login_required
def feed(request):
    queryset = get_feed_queryset(user=request.user)

    posts_filter = PostFilter(
        request.GET,
        queryset=queryset
    )

    paginator = Paginator(
        posts_filter.qs, getattr(settings, 'POSTS_PER_PAGE', 5)
    )
    page = request.GET.get('page', 1)

    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    if request.headers.get('HX-Request'):
        template_name = 'posts/includes/posts_list.html'
    else:
        template_name = 'posts/feed.html'

    context = {
        'posts': posts,
        'filter': posts_filter,
    }

    return render(request, template_name, context)


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
    post = (
        Post.objects.filter(
            pk=post_id
        )
        .annotate(
            liked=Exists(
                Like.objects.filter(user=request.user, post=OuterRef('pk'))
            ),
            saved=Exists(
                Save.objects.filter(user=request.user, post=OuterRef('pk'))
            ),
            comments_count=Count('comments'),
            likes_count=Count('likes'),
        )
        .prefetch_related(
            'media', 'tags', 'likes', 'comments'
        )
        .select_related(
            'author', 'author__profile'
        )
    ).first()

    if not post:
        raise Http404()
    
    root_comments = (
        post.comments.filter(
            level=0
        )
        .order_by('-created')
        .annotate(
            has_children=Exists(
                Comment.objects.filter(parent=OuterRef('pk'))
            )
        )
    )

    paginator = Paginator(
        root_comments,
        per_page=getattr(settings, 'COMMENTS_PER_PAGE', 10)
    )

    page = request.GET.get('page', 1)
    comments_page = paginator.get_page(page)

    if request.headers.get('HX-Request') and request.GET.get('page'):
        template_name = 'posts/includes/comments_list.html'
    else:
        template_name = 'posts/partials/post_preview.html'

    context = {
        'post': post,
        'comment_form': CommentForm(),
        'comments_page': comments_page,
    }

    return render(request, template_name=template_name, context=context)


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


@login_required
def load_replies(request, parent_id):
    parent = get_object_or_404(Comment, pk=parent_id)

    children = (
        parent.get_children()
        .annotate(
            has_children=Exists(
                Comment.objects.filter(parent=OuterRef('pk'))
            )
        )
        .select_related(
            'author', 'author__profile'
        )
    )

    context = {
        'comments': children,
    }

    return render(request, 'posts/partials/replies.html', context)


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

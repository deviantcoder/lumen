from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Exists, OuterRef
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from .models import Story

from apps.profiles.models import Follow
from apps.chat.models import Message, Chat


User = get_user_model()


@login_required
def stories_list(request):
    user = request.user
    now = timezone.now()

    following_ids = user.following.values_list('user__pk', flat=True)

    active_stories_subquery = Story.objects.filter(
        author=OuterRef('pk'),
        expires_at__gt=now
    )

    users = (
        User.objects.filter(pk__in=following_ids)
        .annotate(
            has_active_stories = Exists(
                active_stories_subquery
            )
        )
        .filter(
            has_active_stories=True
        )
        .select_related(
            'profile'
        )
        .prefetch_related(
            'stories'
        )
    )

    context = {
        'users': users,
    }

    return render(request, 'stories/partials/stories_list.html', context)


@login_required
def stories(request, username, story_id=None):
    user = get_object_or_404(User, username=username)

    user_stories = user.stories.order_by('created')

    if not user_stories:
        return redirect('/')

    if story_id:
        current_story = get_object_or_404(user_stories, pk=story_id)
    else:
        current_story = user_stories.first()

    stories_list = list(user_stories)

    try:
        idx = stories_list.index(current_story)
    except ValueError:
        current_story = stories_list[0]
        idx = 0

    prev_story = stories_list[idx - 1] if idx > 0 else None
    next_story = stories_list[idx + 1] if idx < (len(stories_list) - 1) else None

    context = {
        'stories': user_stories,
        'story': current_story,
        'prev_story': prev_story,
        'next_story': next_story,
        'current_idx': idx,
    }

    if request.htmx:
        return render(request, 'stories/partials/story.html', context)

    return render(request, 'stories/stories.html', context)


@login_required
def create_story(request):
    if request.method == 'POST':
        files = request.FILES.getlist('files')

        for file in files:
            story = Story.objects.create(
                author=request.user,
                media=file
            )

            return redirect('stories:stories_with_id', request.user.username, story.pk)

    context = {}

    return render(request, 'stories/partials/story_form.html', context)


@login_required
def share_story(request, story_id):
    story = get_object_or_404(Story, pk=story_id)

    mutuals = User.objects.annotate(
        followed_=Exists(
            Follow.objects.filter(follower=request.user, user=OuterRef('pk'))
        ),
    ).filter(
        followed_=True,
    ).select_related('profile')

    context = {
        'mutuals': mutuals,
        'story': story,
    }

    return render(request, 'stories/partials/share.html', context)


@require_http_methods(['POST'])
@login_required
def send_story_to_chat(request, story_id):
    if request.method == 'POST':
        story = get_object_or_404(Story, pk=story_id)
        usernames = request.POST.get('recipients', '').split(',')

        recipients = User.objects.filter(username__in=usernames)

        for user in recipients:
            chat = Chat.objects.filter(members=request.user).filter(members=user).first()

            if not chat:
                chat = Chat.objects.create()
                chat.members.add(request.user, user)

            Message.objects.create(
                message_type=Message.MESSAGE_TYPES.STORY,
                chat=chat,
                sender=request.user,
                story=story
            )

        return render(request, 'stories/partials/share_success.html')


@require_http_methods(['POST'])
@login_required
def send_story_reply(request, story_id):
    
    story = get_object_or_404(Story, pk=story_id)

    chat = Chat.objects.filter(members=request.user).filter(members=story.author).first()

    if not chat:
        chat = Chat.objects.create()
        chat.members.add(request.user, story.author)

    reply = request.POST.get('reply', '')

    Message.objects.create(
        message_type=Message.MESSAGE_TYPES.STORY_REPLY,
        chat=chat,
        sender=request.user,
        story=story,
        content=reply
    )

    return redirect('/')


@login_required
def collections_list(request, username):
    user = get_object_or_404(User, username=username)
    collections = user.collections.all()

    context = {
        'collections': collections,
    }

    return render(request, 'stories/partials/collections_list.html', context)

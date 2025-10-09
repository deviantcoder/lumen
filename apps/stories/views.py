from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Exists, OuterRef
from django.utils import timezone

from .models import Story


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

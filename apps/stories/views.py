from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Exists, OuterRef
from django.utils import timezone
from django.http import JsonResponse

from .forms import StoryForm
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

    user_stories = user.stories.order_by('-created')

    if story_id:
        current_story = get_object_or_404(user_stories, pk=story_id)
    else:
        current_story = user_stories.first()

    print(current_story)

    stories_list = list(user_stories)

    idx = stories_list.index(current_story)
    prev_story = stories_list[idx - 1] if idx > 0 else None
    next_story = stories_list[idx + 1] if idx < (len(stories_list) - 1) else None

    context = {
        'story': current_story,
        'prev_story': prev_story,
        'next_story': next_story,
    }

    return render(request, 'stories/stories.html', context)


@login_required
def create_story(request):
    # form = StoryForm()

    if request.method == 'POST':
        files = request.FILES.getlist('files')

        for file in files:
            Story.objects.create(
                author=request.user,
                media=file
            )

            messages.success(request, 'Created a story.')

            return redirect('/')

    context = {
        # 'form': form,
    }

    return render(request, 'stories/partials/story_form.html', context)

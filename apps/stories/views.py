from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Exists, OuterRef
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse

from .models import Story, Collection
from .forms import CollectionForm

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


@login_required
def create_collection(request):
    if request.method == 'POST':
        form = CollectionForm(request.POST, request.FILES)
        if form.is_valid():
            collection = form.save(commit=False)
            collection.owner = request.user

            collection.save()
            
            response = HttpResponse(status=204)
            response['HX-Trigger'] = 'close'

            return response
    else:
        form = CollectionForm()

    context = {
        'form': form,
    }

    return render(request, 'stories/partials/collection_form.html', context)


@login_required
def save_story_to_collection(request, story_id):
    story = get_object_or_404(Story, pk=story_id)
    collections = request.user.collections.exclude(stories=story)

    if request.method == 'POST':
        pks = request.POST.get('recipients', '')
        
        pk_list = [int(pk) for pk in pks.split(',') if pk.isdigit()]

        if pk_list:
            collections = Collection.objects.filter(owner=request.user, pk__in=pk_list)

            for collection in collections:
                collection.stories.add(story)

        response = HttpResponse(status=204)
        response['HX-Trigger'] = 'close'

        return response
    
    context = {
        'collections': collections,
        'story': story,
    }

    return render(request, 'stories/partials/save.html', context)


@login_required
def delete_story(request, story_id):
    story = get_object_or_404(Story, pk=story_id)

    if request.method == 'POST':
        story.delete()
        return redirect('stories:stories', request.user.username)
    
    context = {
        'story': story,
    }
    
    return render(request, 'stories/partials/delete_story.html', context)


@login_required
def collection(request, collection_uid, story_id=None):
    collection = get_object_or_404(Collection, public_id=collection_uid)
    stories = collection.stories.all()

    stories_list = list(stories)

    if stories:
        if story_id:
            current_story = get_object_or_404(stories, pk=story_id)
        else:
            current_story = stories.first()

        try:
            idx = stories_list.index(current_story)
        except ValueError:
            current_story = stories_list[0]
            idx = 0
        except IndexError:
            current_story = None
            idx = 0

        prev_story = stories_list[idx - 1] if idx > 0 else None
        next_story = stories_list[idx + 1] if idx < (len(stories_list) - 1) else None
    else:
        context = {
            'collection': collection,
            'stories': [],
            'story': None,
            'prev_story': None,
            'next_story': None,
            'current_idx': None,
            'is_empty': True,
        }

        return render(request, 'stories/collection.html', context)

    context = {
        'collection': collection,
        'stories': stories,
        'story': current_story,
        'prev_story': prev_story,
        'next_story': next_story,
        'current_idx': idx,
        'is_empty': False,
    }
    
    if request.htmx:
        return render(request, 'stories/partials/story.html', context)

    return render(request, 'stories/collection.html', context)


@require_http_methods(['POST'])
@login_required
def remove_story_from_collection(request, collection_uid, story_id):
    collection = get_object_or_404(Collection, public_id=collection_uid)
    story = get_object_or_404(Story, pk=story_id)

    collection.stories.remove(story)

    return redirect('stories:collection', collection.public_id)


@login_required
def edit_collection(request, collection_id):
    collection = get_object_or_404(Collection, pk=collection_id)

    if request.method == 'POST':
        form = CollectionForm(request.POST, request.FILES, instance=collection)
        if form.is_valid():
            print(form.cleaned_data)
            form.save()
            return redirect('stories:collection', collection.public_id)
    else:
        form = CollectionForm(instance=collection)

    context = {
        'form': form,
        'collection': collection,
    }

    return render(request, 'stories/partials/edit_collection.html', context)

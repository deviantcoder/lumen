from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import StoryForm
from .models import Story


User = get_user_model()


@login_required
def stories(request):
    story = Story.objects.first()
    context = {
        'story': story,
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

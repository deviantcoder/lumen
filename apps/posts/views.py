from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import PostForm
from .models import PostMedia



@login_required
def create_post(request):
    form = PostForm()

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            files = form.cleaned_data.get('files', None)

            post = form.save(commit=False)
            post.author = request.user
            post.save()

            if files is not None:
                for file in files:
                    PostMedia.objects.create(
                        post=post,
                        file=file,
                    )

            messages.success(request, 'Post created!')

            return redirect('/')

    context = {
        'form': form,
    }

    return render(request, 'posts/post_form.html', context)

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import PostForm



@login_required
def create_post(request):
    form = PostForm()

    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()

            messages.success(request, 'Post created!')

            return redirect('/')

    context = {
        'form': form,
    }

    return render(request, 'posts/post_form.html', context)

from django import forms

from .models import Post, Comment, Tag


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('widget', MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = [single_file_clean(data, initial)]

        return result


class PostForm(forms.ModelForm):
    files = MultipleFileField()

    class Meta:
        model = Post
        fields = ('caption', 'files')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['caption'].widget.attrs.update({'placeholder': 'Add caption...'})


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('body', 'parent')
        widgets = {
            'body': forms.TextInput(attrs={'placeholder': 'Write a comment...'}),
            'parent': forms.HiddenInput()
        }


class EditPostForm(forms.ModelForm):
    tags_ = forms.CharField(
        widget=forms.TextInput(),
        required=False
    )

    class Meta:
        model = Post
        fields = ('caption', 'tags_')

    def __init__(self, *args, **kwargs):
        tags_ = kwargs.pop('tags_', None)

        super().__init__(*args, **kwargs)

        if tags_:
            self.initial['tags_'] = tags_

        self.fields['caption'].widget.attrs.update({'placeholder': 'Add caption...'})
        self.fields['tags_'].widget.attrs.update({'placeholder': 'Add tags'})

    def save(self, commit=True):
        post = super().save(commit=False)

        tags_str = self.cleaned_data.get('tags_', '')
        tag_names = [tag.strip().lower() for tag in tags_str.split('#') if tag.strip()]

        if commit:
            post.save()
            post.tags.clear()

            for name in tag_names:
                tag, _ = Tag.objects.get_or_create(name=name)
                post.tags.add(tag)

        return post

from django import forms

from .models import Post, Comment


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
        self.fields['caption'].widget.attrs.update({'placeholder': 'Enter a post caption...'})


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('body', 'parent')
        widgets = {
            'body': forms.TextInput(attrs={'placeholder': 'Write a comment...'}),
            'parent': forms.HiddenInput()
        }
    
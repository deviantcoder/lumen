from django import forms

from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('caption',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['caption'].widget.attrs.update({'placeholder': 'Enter a post caption...'})
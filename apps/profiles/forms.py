from django import forms

from .models import Profile


class URLForm(forms.ModelForm):
    
    class Meta:
        model = Profile
        fields = ('url',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['url'].widget.attrs.update({'placeholder': 'Website link'})


class BioForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = ('bio',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['bio'].widget.attrs.update({'placeholder': 'Enter your bio'})

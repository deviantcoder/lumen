from django import forms

from .models import Collection


class CollectionForm(forms.ModelForm):
    class Meta:
        model = Collection
        fields = ('name', 'image')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['name'].widget.attrs.update({'placeholder': 'Name your collection'})

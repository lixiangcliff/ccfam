from django import forms
from .models import Photo

class PhotoForm(forms.ModelForm):
    image = forms.ImageField(label='Image')

    class Meta:
        model = Photo
        fields = [
            'author',
            'editor',
            'album',
            'description',
            'image',
        ]

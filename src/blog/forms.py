from django import forms
from .models import Album, Photo


class AlbumForm(forms.ModelForm):

    class Meta:
        model = Album
        fields = [
            'title',
            'author',
            'description',
            'image',
            'draft',
        ]


class PhotoForm(forms.ModelForm):
    image = forms.ImageField(label='Image')

    class Meta:
        model = Photo
        fields = [
            #'title',
            'author',
            'editor',
            'image',
            'description',
            #'device_make',
        ]
